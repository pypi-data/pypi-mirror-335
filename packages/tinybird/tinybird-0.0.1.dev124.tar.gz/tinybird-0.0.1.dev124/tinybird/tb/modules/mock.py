import glob
from pathlib import Path

import click

from tinybird.prompts import mock_prompt
from tinybird.tb.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import CLIException, coro, push_data
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import persist_fixture, persist_fixture_sql
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml
from tinybird.tb.modules.project import Project


@cli.command()
@click.argument("datasource", type=str)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@click.option(
    "--prompt",
    type=str,
    default="",
    help="Extra context to use for data generation",
)
@click.pass_context
@coro
async def mock(ctx: click.Context, datasource: str, rows: int, prompt: str) -> None:
    """Generate sample data for a data source.

    Args:
        datasource: Path to the datasource file to load sample data into
        rows: Number of events to send
        prompt: Extra context to use for data generation
        skip: Skip following up on the generated data
    """

    try:
        tb_client: TinyB = ctx.ensure_object(dict)["client"]
        project: Project = ctx.ensure_object(dict)["project"]
        ctx_config = ctx.ensure_object(dict)["config"]
        env = ctx.ensure_object(dict)["env"]
        datasource_path = Path(datasource)
        datasource_name = datasource
        folder = project.folder
        click.echo(FeedbackManager.highlight(message=f"\n» Creating fixture for {datasource_name}..."))
        if datasource_path.suffix == ".datasource":
            datasource_name = datasource_path.stem
        else:
            datasource_from_glob = glob.glob(f"{folder}/**/{datasource}.datasource")
            if datasource_from_glob:
                datasource_path = Path(datasource_from_glob[0])

        if not datasource_path.exists():
            raise CLIException(f"Datasource '{datasource_path.stem}' not found")

        datasource_content = datasource_path.read_text()
        config = CLIConfig.get_project_config()
        user_client = config.get_client(token=ctx_config.get("token"), host=ctx_config.get("host"))
        user_token = ctx_config.get("user_token")

        try:
            if not user_token:
                raise CLIException("No user token found")
        except Exception:
            click.echo(FeedbackManager.error(message="This action requires authentication. Run 'tb login' first."))
            return

        llm = LLM(user_token=user_token, host=user_client.host)
        prompt = f"<datasource_schema>{datasource_content}</datasource_schema>\n<user_input>{prompt}</user_input>"
        sql = ""
        attempts = 0
        data = []
        error = ""
        sql_path = None
        while True:
            try:
                response = llm.ask(system_prompt=mock_prompt(rows, error), prompt=prompt)
                sql = extract_xml(response, "sql")
                sql_path = persist_fixture_sql(datasource_name, sql, folder)
                result = await tb_client.query(f"{sql} FORMAT JSON")
                data = result.get("data", [])[:rows]
                error_response = result.get("error", None)
                if error_response:
                    raise CLIException(error_response)
                else:
                    break
            except Exception as e:
                error = str(e)
                attempts += 1
                if attempts > 5:
                    raise Exception(f"Failed to generate a valid solution. Check {str(sql_path)} and try again.")
                else:
                    continue

        fixture_path = persist_fixture(datasource_name, data, folder)
        click.echo(FeedbackManager.info(message=f"✓ /fixtures/{datasource_name}.ndjson created"))
        if env == "cloud":
            await append_fixture(tb_client, datasource_name, str(fixture_path))

        click.echo(FeedbackManager.success(message=f"✓ Sample data for {datasource_name} created with {rows} rows"))

    except Exception as e:
        click.echo(FeedbackManager.error_exception(error=f"Error: {e}"))


async def append_fixture(
    tb_client: TinyB,
    datasource_name: str,
    url: str,
):
    await push_data(
        tb_client,
        datasource_name,
        url,
        mode="append",
        concurrency=1,
        silent=True,
    )
