import os
import re
from pathlib import Path
from typing import Optional, Tuple

import click

from tinybird.prompts import create_prompt, mock_prompt, readme_prompt, rules_prompt
from tinybird.tb.client import TinyB
from tinybird.tb.modules.cicd import init_cicd
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import _generate_datafile, coro, generate_datafile
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import persist_fixture
from tinybird.tb.modules.exceptions import CLIException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml, parse_xml
from tinybird.tb.modules.project import Project


@cli.command()
@click.option(
    "--data",
    type=click.Path(exists=True),
    default=None,
    help="Initial data to be used to create the project",
)
@click.option(
    "--prompt",
    type=str,
    default=None,
    help="Prompt to be used to create the project",
)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@click.option("--folder", type=str, default=None, help="Folder to create the project in")
@click.option("--agent", type=str, default="cursor", help="Agent to use for rules")
@click.pass_context
@coro
async def create(
    ctx: click.Context, data: Optional[str], prompt: Optional[str], rows: int, folder: Optional[str], agent: str
) -> None:
    """Initialize a new project."""
    local_client: TinyB = ctx.ensure_object(dict)["client"]
    project: Project = ctx.ensure_object(dict)["project"]
    config = CLIConfig.get_project_config()
    ctx_config = ctx.ensure_object(dict)["config"]

    # If folder is provided, rewrite the config and project folder
    if folder:
        config.set_cwd(folder)
        config.persist_to_file()
        project.folder = folder

    if cwd := config.get("cwd"):
        click.echo(FeedbackManager.gray(message=f"Using '{cwd.replace(os.getcwd(), '')}' as target folder"))

    root_folder = os.getcwd()
    if config._path:
        root_folder = os.path.dirname(config._path)

    folder = project.folder
    folder_path = project.path

    if not folder_path.exists():
        folder_path.mkdir()

    try:
        tb_client = config.get_client(token=ctx_config.get("token"), host=ctx_config.get("host"))
        user_token: Optional[str] = None
        created_something = False
        if prompt:
            try:
                user_token = ctx_config.get("user_token")
                if not user_token:
                    raise CLIException("No user token found")
            except Exception as e:
                click.echo(
                    FeedbackManager.error(
                        message=f"This action requires authentication. Run 'tb login' first. Error: {e}"
                    )
                )
                return

        if not validate_project_structure(folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating new project structure..."))
            create_project_structure(folder)
            click.echo(FeedbackManager.success(message="✓ Scaffolding completed!\n"))
            created_something = True
        result = ""
        if (data or prompt) and user_token:
            click.echo(FeedbackManager.highlight(message="\n» Creating resources..."))
            result, created_something = await create_resources(
                local_client, tb_client, user_token, data, prompt, folder
            )
            click.echo(FeedbackManager.success(message="✓ Done!\n"))
            if prompt:
                readme_path = Path(root_folder) / "README.md"
                if readme_path.exists():
                    click.echo(FeedbackManager.highlight(message="\n» Updating README.md..."))
                else:
                    click.echo(FeedbackManager.highlight(message="\n» Creating README.md..."))
                    readme_path.touch()
                llm = LLM(user_token=str(user_token), host=tb_client.host)
                readme_user_prompt = prompt or ""
                all_resources_xml = get_resources_xml(project)
                readme_response = llm.ask(
                    system_prompt=readme_prompt(
                        readme_path.read_text(), tb_client.host, "$TB_ADMIN_TOKEN", all_resources_xml
                    ),
                    prompt=readme_user_prompt,
                )
                readme_result = extract_xml(readme_response, "readme")
                readme_path.write_text(readme_result)
                click.echo(FeedbackManager.success(message="✓ Done!\n"))
                created_something = True

        if not already_has_cicd(root_folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating CI/CD files for GitHub and GitLab..."))
            init_git(root_folder)
            await init_cicd(root_folder, data_project_dir=os.path.relpath(folder))
            click.echo(FeedbackManager.success(message="✓ Done!\n"))
            created_something = True

        if not already_has_cursor_rules(root_folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating .cursorrules..."))
            create_rules(root_folder, "tb", agent)
            click.echo(FeedbackManager.success(message="✓ Done!\n"))
            created_something = True

        if should_generate_fixtures(result):
            click.echo(FeedbackManager.highlight(message="\n» Generating fixtures..."))

            if data:
                ds_name = os.path.basename(data.split(".")[0])
                data_content = Path(data).read_text()
                datasource_path = Path(folder) / "datasources" / f"{ds_name}.datasource"
                click.echo(FeedbackManager.info(message=f"✓ /fixtures/{ds_name}"))
                persist_fixture(ds_name, data_content, folder)
                created_something = True
            elif prompt and user_token:
                datasource_files = [f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")]
                for datasource_file in datasource_files:
                    datasource_path = Path(folder) / "datasources" / datasource_file
                    llm = LLM(user_token=user_token, host=tb_client.host)
                    datasource_name = datasource_path.stem
                    datasource_content = datasource_path.read_text()
                    has_json_path = "`json:" in datasource_content
                    if has_json_path:
                        prompt = f"<datasource_schema>{datasource_content}</datasource_schema>"
                        response = llm.ask(system_prompt=mock_prompt(rows), prompt=prompt)
                        sql = extract_xml(response, "sql")
                        sql = sql.split("FORMAT")[0]
                        query_result = await local_client.query(f"{sql} FORMAT JSON")
                        data = query_result.get("data", [])
                        if data:
                            persist_fixture(datasource_name, data, folder)
                            click.echo(FeedbackManager.info(message=f"✓ /fixtures/{datasource_name}"))
                            created_something = True

        if not created_something:
            click.echo(FeedbackManager.warning(message="△ No resources created\n"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Error: {str(e)}"))


PROJECT_PATHS = ("datasources", "endpoints", "materializations", "copies", "pipes", "fixtures", "tests", "connections")


def validate_project_structure(folder: str) -> bool:
    some_folder_created = any((Path(folder) / path).exists() for path in PROJECT_PATHS)
    if some_folder_created:
        return True

    folder_path = Path(folder)
    datasources = list(folder_path.glob("**/*.datasource"))
    pipes = list(folder_path.glob("**/*.pipe"))

    return len(datasources) > 0 or len(pipes) > 0


def should_generate_fixtures(result: str) -> bool:
    if not result:
        return False
    return "<type>datasource</type>" in result


def already_has_cicd(folder: str) -> bool:
    ci_cd_paths = (".gitlab", ".github")
    return any((Path(folder) / path).exists() for path in ci_cd_paths)


def already_has_cursor_rules(folder: str) -> bool:
    cursor_rules_paths = (".cursorrules", ".windsurfrules")
    return any((Path(folder) / path).exists() for path in cursor_rules_paths)


def create_project_structure(folder: str):
    folder_path = Path(folder)
    for x in PROJECT_PATHS:
        try:
            f = folder_path / x
            f.mkdir()
        except FileExistsError:
            pass
        click.echo(FeedbackManager.info_path_created(path=x))


async def create_resources(
    local_client: TinyB,
    tb_client: TinyB,
    user_token: Optional[str],
    data: Optional[str],
    prompt: Optional[str],
    folder: str,
) -> Tuple[str, bool]:
    result = ""
    created_any_resource = False
    folder_path = Path(folder)
    if data:
        path = folder_path / data
        format = path.suffix.lstrip(".")
        await _generate_datafile(str(path), local_client, format=format, force=True)
        name = data.split(".")[0]
        generate_pipe_file(
            f"{name}_endpoint",
            f"""
NODE endpoint
SQL >
    SELECT * from {name}
TYPE ENDPOINT
            """,
            folder,
        )
        result = (
            f"<response><resource><type>datasource</type><name>{name}</name><content></content></resource></response>"
        )
        created_any_resource = True

    elif prompt and user_token:
        datasource_paths = [
            Path(folder) / "datasources" / f
            for f in os.listdir(Path(folder) / "datasources")
            if f.endswith(".datasource")
        ]
        pipes_paths = [
            Path(folder) / "endpoints" / f for f in os.listdir(Path(folder) / "endpoints") if f.endswith(".pipe")
        ]
        resources_xml = "\n".join(
            [
                f"<resource><type>{resource_type}</type><name>{resource_name}</name><content>{resource_content}</content></resource>"
                for resource_type, resource_name, resource_content in [
                    ("datasource", ds.stem, ds.read_text()) for ds in datasource_paths
                ]
                + [
                    (
                        "pipe",
                        pipe.stem,
                        pipe.read_text(),
                    )
                    for pipe in pipes_paths
                ]
            ]
        )
        llm = LLM(user_token=user_token, host=tb_client.host)
        result = llm.ask(system_prompt=create_prompt(resources_xml), prompt=prompt)
        result = extract_xml(result, "response")
        resources = parse_xml(result, "resource")
        datasources = []
        pipes = []
        connections = []
        for resource_xml in resources:
            resource_type = extract_xml(resource_xml, "type")
            name = extract_xml(resource_xml, "name")
            content = extract_xml(resource_xml, "content")
            resource = {
                "name": name,
                "content": content,
            }
            if resource_type.lower() == "datasource":
                datasources.append(resource)
            elif resource_type.lower() == "pipe":
                pipes.append(resource)
            elif resource_type.lower() == "connection":
                connections.append(resource)

        for ds in datasources:
            content = ds["content"].replace("```", "")
            filename = f"{ds['name']}.datasource"
            generate_datafile(
                content,
                filename=filename,
                data=None,
                _format="ndjson",
                force=True,
                folder=folder,
            )
            created_any_resource = True

        for pipe in pipes:
            content = pipe["content"].replace("```", "")
            generate_pipe_file(pipe["name"], content, folder)
            created_any_resource = True

        for conn in connections:
            content = conn["content"].replace("```", "")
            filename = f"{conn['name']}.connection"
            generate_connection_file(conn["name"], content, folder)
            created_any_resource = True

    return result, created_any_resource


def init_git(folder: str):
    try:
        path = Path(folder)
        gitignore_file = path / ".gitignore"

        if gitignore_file.exists():
            content = gitignore_file.read_text()
            if ".tinyb" not in content:
                gitignore_file.write_text(content + "\n.tinyb\n.terraform\n")
        else:
            gitignore_file.write_text(".tinyb\n.terraform\n")

        click.echo(FeedbackManager.info_file_created(file=".gitignore"))
    except Exception as e:
        raise CLIException(f"Error initializing Git: {e}")


def generate_pipe_file(name: str, content: str, folder: str) -> Path:
    def is_copy(content: str) -> bool:
        return re.search(r"TYPE copy", content, re.IGNORECASE) is not None

    def is_materialization(content: str) -> bool:
        return re.search(r"TYPE materialized", content, re.IGNORECASE) is not None

    def is_sink(content: str) -> bool:
        return re.search(r"TYPE sink", content, re.IGNORECASE) is not None

    def is_endpoint(content: str) -> bool:
        return re.search(r"TYPE endpoint", content, re.IGNORECASE) is not None

    if is_copy(content):
        pathname = "copies"
    elif is_materialization(content):
        pathname = "materializations"
    elif is_sink(content):
        pathname = "sinks"
    elif is_endpoint(content):
        pathname = "endpoints"
    else:
        pathname = "pipes"

    base = Path(folder) / pathname
    if not base.exists():
        base = Path()
    f = base / (f"{name}.pipe")
    with open(f"{f}", "w") as file:
        file.write(content)
    click.echo(FeedbackManager.info_file_created(file=f.relative_to(folder)))
    return f.relative_to(folder)


def generate_connection_file(name: str, content: str, folder: str, skip_feedback: bool = False) -> Path:
    base = Path(folder) / "connections"
    if not base.exists():
        base.mkdir()
    f = base / (f"{name}.connection")
    with open(f"{f}", "w") as file:
        file.write(content)
    if not skip_feedback:
        click.echo(FeedbackManager.info_file_created(file=f.relative_to(folder)))
    return f.relative_to(folder)


async def generate_aws_iamrole_connection_file_with_secret(
    name: str, service: str, role_arn_secret_name: str, region: str, folder: str
) -> Path:
    content = f"""TYPE {service}
S3_ARN {{{{ tb_secret("{role_arn_secret_name}") }}}}
S3_REGION {region}
"""
    file_path = generate_connection_file(name, content, folder, skip_feedback=True)
    return file_path


def create_rules(folder: str, source: str, agent: str):
    if agent == "cursor":
        extension = ".cursorrules"
    elif agent == "windsurf":
        extension = ".windsurfrules"
    else:
        extension = ".txt"
    rules_file = Path(folder) / extension
    rules_file.write_text(rules_prompt(source))


def get_context_file() -> Path:
    context_file = Path(os.path.expanduser("~/.tb_create_context"))
    if not context_file.exists():
        context_file.touch()
    return context_file


def get_context() -> str:
    context_file = get_context_file()
    return context_file.read_text()


def save_context(prompt: str, feedback: str):
    context_file = get_context_file()
    context_file.write_text(f"- {prompt}\n{feedback}")


def get_resources_xml(project: Project) -> str:
    folder = project.folder
    datasource_paths = [
        Path(folder) / "datasources" / f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")
    ]
    pipes_paths = [
        Path(folder) / "endpoints" / f for f in os.listdir(Path(folder) / "endpoints") if f.endswith(".pipe")
    ]
    resources_xml = "\n".join(
        [
            f"<resource><type>{resource_type}</type><name>{resource_name}</name><content>{resource_content}</content></resource>"
            for resource_type, resource_name, resource_content in [
                ("datasource", ds.stem, ds.read_text()) for ds in datasource_paths
            ]
            + [
                (
                    "pipe",
                    pipe.stem,
                    pipe.read_text(),
                )
                for pipe in pipes_paths
            ]
        ]
    )
    return resources_xml
