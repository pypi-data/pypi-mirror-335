import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import click
import requests

from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import echo_safe_humanfriendly_tables_format_smart_table, get_display_cloud_host
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.project import Project


# TODO(eclbg): This should eventually end up in client.py, but we're not using it here yet.
def api_fetch(url: str, headers: dict) -> dict:
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        logging.debug(json.dumps(r.json(), indent=2))
        return r.json()
    # Try to parse and print the error from the response
    try:
        result = r.json()
        error = result.get("error")
        logging.debug(json.dumps(result, indent=2))
        click.echo(FeedbackManager.error(message=f"Error: {error}"))
        sys.exit(1)
    except Exception:
        click.echo(FeedbackManager.error(message="Error parsing response from API"))
        sys.exit(1)


def api_post(
    url: str,
    headers: dict,
    files: Optional[list] = None,
    params: Optional[dict] = None,
) -> dict:
    r = requests.post(url, headers=headers, files=files, params=params)
    if r.status_code < 300:
        logging.debug(json.dumps(r.json(), indent=2))
        return r.json()
    # Try to parse and print the error from the response
    try:
        result = r.json()
        logging.debug(json.dumps(result, indent=2))
        error = result.get("error")
        if error:
            click.echo(FeedbackManager.error(message=f"Error: {error}"))
            sys.exit(1)
        return result
    except Exception:
        click.echo(FeedbackManager.error(message="Error parsing response from API"))
        sys.exit(1)


# TODO(eclbg): This logic should be in the server, and there should be a dedicated endpoint for promoting a deployment
# potato
def promote_deployment(host: Optional[str], headers: dict, wait: bool) -> None:
    TINYBIRD_API_URL = f"{host}/v1/deployments"
    result = api_fetch(TINYBIRD_API_URL, headers)

    deployments = result.get("deployments")
    if not deployments:
        click.echo(FeedbackManager.error(message="No deployments found"))
        sys.exit(1)

    if len(deployments) < 2:
        click.echo(FeedbackManager.error(message="Only one deployment found"))
        sys.exit(1)

    last_deployment, candidate_deployment = deployments[0], deployments[1]

    if candidate_deployment.get("status") != "data_ready":
        click.echo(FeedbackManager.error(message="Current deployment is not ready"))
        deploy_errors = candidate_deployment.get("errors", [])
        for deploy_error in deploy_errors:
            click.echo(FeedbackManager.error(message=f"* {deploy_error}"))
        sys.exit(1)

    if candidate_deployment.get("live"):
        click.echo(FeedbackManager.error(message="Candidate deployment is already live"))
    else:
        click.echo(FeedbackManager.success(message="Setting candidate deployment as live"))

        TINYBIRD_API_URL = f"{host}/v1/deployments/{candidate_deployment.get('id')}/set-live"
        result = api_post(TINYBIRD_API_URL, headers=headers)

    click.echo(FeedbackManager.success(message="Removing old deployment"))

    TINYBIRD_API_URL = f"{host}/v1/deployments/{last_deployment.get('id')}"
    r = requests.delete(TINYBIRD_API_URL, headers=headers)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))
    if result.get("error"):
        click.echo(FeedbackManager.error(message=result.get("error")))
        sys.exit(1)

    click.echo(FeedbackManager.success(message="Deployment promotion successfully started"))

    if wait:
        while True:
            TINYBIRD_API_URL = f"{host}/v1/deployments/{last_deployment.get('id')}"
            result = api_fetch(TINYBIRD_API_URL, headers=headers)

            last_deployment = result.get("deployment")
            if last_deployment.get("status") == "deleted":
                click.echo(FeedbackManager.success(message="Deployment promoted successfully"))
                break

            time.sleep(5)


# TODO(eclbg): This logic should be in the server, and there should be a dedicated endpoint for discarding a
# deployment
def discard_deployment(host: Optional[str], headers: dict, wait: bool) -> None:
    TINYBIRD_API_URL = f"{host}/v1/deployments"
    result = api_fetch(TINYBIRD_API_URL, headers=headers)

    deployments = result.get("deployments")
    if not deployments:
        click.echo(FeedbackManager.error(message="No deployments found"))
        return

    if len(deployments) < 2:
        click.echo(FeedbackManager.error(message="Only one deployment found"))
        return

    previous_deployment, current_deployment = deployments[0], deployments[1]

    if previous_deployment.get("status") != "data_ready":
        click.echo(FeedbackManager.error(message="Previous deployment is not ready"))
        deploy_errors = previous_deployment.get("errors", [])
        for deploy_error in deploy_errors:
            click.echo(FeedbackManager.error(message=f"* {deploy_error}"))
        return

    if previous_deployment.get("live"):
        click.echo(FeedbackManager.error(message="Previous deployment is already live"))
    else:
        click.echo(FeedbackManager.success(message="Promoting previous deployment"))

        TINYBIRD_API_URL = f"{host}/v1/deployments/{previous_deployment.get('id')}/set-live"
        result = api_post(TINYBIRD_API_URL, headers=headers)

    click.echo(FeedbackManager.success(message="Removing current deployment"))

    TINYBIRD_API_URL = f"{host}/v1/deployments/{current_deployment.get('id')}"
    r = requests.delete(TINYBIRD_API_URL, headers=headers)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))
    if result.get("error"):
        click.echo(FeedbackManager.error(message=result.get("error")))
        sys.exit(1)

    click.echo(FeedbackManager.success(message="Discard process successfully started"))

    if wait:
        while True:
            TINYBIRD_API_URL = f"{host}/v1/deployments/{current_deployment.get('id')}"
            result = api_fetch(TINYBIRD_API_URL, headers)

            current_deployment = result.get("deployment")
            if current_deployment.get("status") == "deleted":
                click.echo(FeedbackManager.success(message="Discard process successfully completed"))
                break
            time.sleep(5)


@cli.group(name="deployment")
def deployment_group() -> None:
    """
    Deployment commands.
    """
    pass


@deployment_group.command(name="create")
@click.option(
    "--wait/--no-wait",
    is_flag=True,
    default=False,
    help="Wait for deploy to finish. Disabled by default.",
)
@click.option(
    "--auto/--no-auto",
    is_flag=True,
    default=False,
    help="Auto-promote the deployment. Only works if --wait is enabled. Disabled by default.",
)
@click.option(
    "--check/--no-check",
    is_flag=True,
    default=False,
    help="Validate the deployment before creating it. Disabled by default.",
)
@click.option(
    "--allow-destructive-operations/--no-allow-destructive-operations",
    is_flag=True,
    default=False,
    help="Allow removing datasources. Disabled by default.",
)
@click.pass_context
def deployment_create(
    ctx: click.Context, wait: bool, auto: bool, check: bool, allow_destructive_operations: bool
) -> None:
    """
    Validate and deploy the project server side.
    """
    create_deployment(ctx, wait, auto, check, allow_destructive_operations)


@deployment_group.command(name="ls")
@click.option(
    "--include-deleted",
    is_flag=True,
    default=False,
    help="Include deleted deployments. Disabled by default.",
)
@click.pass_context
def deployment_ls(ctx: click.Context, include_deleted: bool) -> None:
    """
    List all the deployments you have in the project.
    """
    client = ctx.ensure_object(dict)["client"]

    TINYBIRD_API_KEY = client.token
    HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}
    url = f"{client.host}/v1/deployments"
    if include_deleted:
        url += "?include_deleted=true"

    result = api_fetch(url, HEADERS)
    status_map = {"data_ready": "Staging", "failed": "Failed", "deleted": "Deleted"}
    columns = ["ID", "Status", "Created at"]
    table = []
    for deployment in result.get("deployments", []):
        if deployment.get("id") == "0":
            continue

        table.append(
            [
                deployment.get("id"),
                "Live" if deployment.get("live") else status_map.get(deployment.get("status", "In progress")),
                datetime.fromisoformat(deployment.get("created_at")).strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    table.reverse()
    echo_safe_humanfriendly_tables_format_smart_table(table, column_names=columns)


@deployment_group.command(name="promote")
@click.pass_context
@click.option(
    "--wait/--no-wait",
    is_flag=True,
    default=False,
    help="Wait for deploy to finish. Disabled by default.",
)
def deployment_promote(ctx: click.Context, wait: bool) -> None:
    """
    Promote last deploy to ready and remove old one.
    """
    client = ctx.ensure_object(dict)["client"]

    TINYBIRD_API_KEY = client.token
    HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}

    promote_deployment(client.host, HEADERS, wait=wait)


@deployment_group.command(name="discard")
@click.pass_context
@click.option(
    "--wait/--no-wait",
    is_flag=True,
    default=False,
    help="Wait for deploy to finish. Disabled by default.",
)
def deployment_discard(ctx: click.Context, wait: bool) -> None:
    """
    Discard the current deployment.
    """
    client = ctx.ensure_object(dict)["client"]

    TINYBIRD_API_KEY = client.token
    HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}

    discard_deployment(client.host, HEADERS, wait=wait)


@cli.command(name="deploy", hidden=True)
@click.option(
    "--wait/--no-wait",
    is_flag=True,
    default=True,
    help="Wait for deploy to finish. Disabled by default.",
)
@click.option(
    "--auto/--no-auto",
    is_flag=True,
    default=True,
    help="Auto-promote or auto-discard the deployment. Only works if --wait is enabled. Disabled by default.",
)
@click.option(
    "--check",
    is_flag=True,
    default=False,
    help="Validate the deployment before creating it. Disabled by default.",
)
@click.option(
    "--allow-destructive-operations/--no-allow-destructive-operations",
    is_flag=True,
    default=False,
    help="Allow removing datasources. Disabled by default.",
)
@click.pass_context
def deploy(ctx: click.Context, wait: bool, auto: bool, check: bool, allow_destructive_operations: bool) -> None:
    """
    Deploy the project.
    """
    create_deployment(ctx, wait, auto, check, allow_destructive_operations)


def create_deployment(
    ctx: click.Context,
    wait: bool,
    auto: bool,
    check: Optional[bool] = None,
    allow_destructive_operations: Optional[bool] = None,
) -> None:
    # TODO: This code is duplicated in build_server.py
    # Should be refactored to be shared
    MULTIPART_BOUNDARY_DATA_PROJECT = "data_project://"
    DATAFILE_TYPE_TO_CONTENT_TYPE = {
        ".datasource": "text/plain",
        ".pipe": "text/plain",
        ".connection": "text/plain",
    }
    project: Project = ctx.ensure_object(dict)["project"]
    client = ctx.ensure_object(dict)["client"]
    config: Dict[str, Any] = ctx.ensure_object(dict)["config"]
    TINYBIRD_API_URL = f"{client.host}/v1/deploy"
    TINYBIRD_API_KEY = client.token

    files = [
        ("context://", ("cli-version", "1.0.0", "text/plain")),
    ]
    fds = []
    for file_path in project.get_project_files():
        relative_path = str(Path(file_path).relative_to(project.path))
        fd = open(file_path, "rb")
        fds.append(fd)
        content_type = DATAFILE_TYPE_TO_CONTENT_TYPE.get(Path(file_path).suffix, "application/unknown")
        files.append((MULTIPART_BOUNDARY_DATA_PROJECT, (relative_path, fd.read().decode("utf-8"), content_type)))

    deployment = None
    try:
        HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}
        params = {}
        if check:
            click.echo(FeedbackManager.highlight(message="\n» Validating deployment...\n"))
            params["check"] = "true"
        if allow_destructive_operations:
            params["allow_destructive_operations"] = "true"

        result = api_post(TINYBIRD_API_URL, headers=HEADERS, files=files, params=params)

        print_changes(result, project)

        deployment = result.get("deployment", {})
        feedback = deployment.get("feedback", [])
        for f in feedback:
            if f.get("level", "").upper() == "ERROR":
                feedback_func = FeedbackManager.error
                feedback_icon = ""
            else:
                feedback_func = FeedbackManager.warning
                feedback_icon = "△ "
            resource = f.get("resource")
            resource_bit = f"{resource}: " if resource else ""
            click.echo(feedback_func(message=f"{feedback_icon}{f.get('level')}: {resource_bit}{f.get('message')}"))

        deploy_errors = deployment.get("errors")
        for deploy_error in deploy_errors:
            if deploy_error.get("filename", None):
                click.echo(
                    FeedbackManager.error(message=f"{deploy_error.get('filename')}\n\n{deploy_error.get('error')}")
                )
            else:
                click.echo(FeedbackManager.error(message=f"{deploy_error.get('error')}"))
        click.echo("")  # For spacing

        status = result.get("result")
        if check:
            if status == "success":
                click.echo(FeedbackManager.success(message="\n✓ Deployment is valid"))
                sys.exit(0)
            elif status == "no_changes":
                sys.exit(0)

            click.echo(FeedbackManager.error(message="\n✗ Deployment is not valid"))
            sys.exit(1)

        status = result.get("result")
        if status == "success":
            host = get_display_cloud_host(client.host)
            click.echo(
                FeedbackManager.gray(message="Deployment URL: ")
                + FeedbackManager.info(message=f"{host}/{config.get('name')}/deployments/{deployment.get('id')}")
            )

            if wait:
                click.echo(FeedbackManager.info(message="\n✓ Deployment submitted successfully"))
            else:
                click.echo(FeedbackManager.success(message="\n✓ Deployment submitted successfully"))
        elif status == "no_changes":
            click.echo(FeedbackManager.highlight(message="Not deploying. No changes."))
            sys.exit(0)
        elif status == "failed":
            click.echo(FeedbackManager.error(message="Deployment failed"))
            sys.exit(1)
        else:
            click.echo(FeedbackManager.error(message=f"Unknown deployment result {status}"))
    except Exception as e:
        click.echo(FeedbackManager.error_exception(error=e))
    finally:
        for fd in fds:
            fd.close()

        if not deployment and not check:
            sys.exit(1)

    if deployment and wait and not check:
        while True:
            url = f"{client.host}/v1/deployments/{deployment.get('id')}"
            res = api_fetch(url, HEADERS)
            deployment = res.get("deployment")
            if not deployment:
                click.echo(FeedbackManager.error(message="Error parsing deployment from response"))
                sys.exit(1)
            if deployment.get("status") == "failed":
                click.echo(FeedbackManager.error(message="Deployment failed"))
                deploy_errors = deployment.get("errors")
                for deploy_error in deploy_errors:
                    click.echo(FeedbackManager.error(message=f"* {deploy_error}"))

                if auto:
                    click.echo(FeedbackManager.error(message="Rolling back deployment"))
                    discard_deployment(client.host, HEADERS, wait=wait)
                sys.exit(1)

            if deployment.get("status") == "data_ready":
                break

            time.sleep(5)

        click.echo(FeedbackManager.success(message="Deployment is ready"))

        if auto:
            promote_deployment(client.host, HEADERS, wait=wait)


def print_changes(result: dict, project: Project) -> None:
    deployment = result.get("deployment", {})
    resources_columns = ["status", "name", "path"]
    resources: list[list[Union[str, None]]] = []
    tokens_columns = ["Change", "Token name", "Added permissions", "Removed permissions"]
    tokens: list[Tuple[str, str, str, str]] = []

    for ds in deployment.get("new_datasource_names", []):
        resources.append(["new", ds, project.get_resource_path(ds, "datasource")])

    for p in deployment.get("new_pipe_names", []):
        resources.append(["new", p, project.get_resource_path(p, "pipe")])

    for dc in deployment.get("new_data_connector_names", []):
        resources.append(["new", dc, project.get_resource_path(dc, "connection")])

    for ds in deployment.get("changed_datasource_names", []):
        resources.append(["modified", ds, project.get_resource_path(ds, "datasource")])

    for p in deployment.get("changed_pipe_names", []):
        resources.append(["modified", p, project.get_resource_path(p, "pipe")])

    for dc in deployment.get("changed_data_connector_names", []):
        resources.append(["modified", dc, project.get_resource_path(dc, "connection")])

    for ds in deployment.get("deleted_datasource_names", []):
        resources.append(["deleted", ds, project.get_resource_path(ds, "datasource")])

    for p in deployment.get("deleted_pipe_names", []):
        resources.append(["deleted", p, project.get_resource_path(p, "pipe")])

    for dc in deployment.get("deleted_data_connector_names", []):
        resources.append(["deleted", dc, project.get_resource_path(dc, "connection")])

    for token_change in deployment.get("token_changes", []):
        token_name = token_change.get("token_name")
        change_type = token_change.get("change_type")
        added_perms = []
        removed_perms = []
        permission_changes = token_change.get("permission_changes", {})
        for perm in permission_changes.get("added_permissions", []):
            added_perms.append(f"{perm['resource_name']}.{perm['resource_type']}:{perm['permission']}")
        for perm in permission_changes.get("removed_permissions", []):
            removed_perms.append(f"{perm['resource_name']}.{perm['resource_type']}:{perm['permission']}")

        tokens.append((change_type, token_name, "\n".join(added_perms), "\n".join(removed_perms)))

    if resources:
        click.echo(FeedbackManager.highlight(message="\n» Changes to be deployed...\n"))
        echo_safe_humanfriendly_tables_format_smart_table(resources, column_names=resources_columns)
    else:
        click.echo(FeedbackManager.highlight(message="\n» No changes to be deployed\n"))
    if tokens:
        click.echo(FeedbackManager.highlight(message="\n» Changes in tokens to be deployed...\n"))
        echo_safe_humanfriendly_tables_format_smart_table(tokens, column_names=tokens_columns)
    else:
        click.echo(FeedbackManager.highlight(message="\n» No changes in tokens to be deployed\n"))
