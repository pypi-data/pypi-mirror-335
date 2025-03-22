import hashlib
import logging
import os
from typing import Any, Dict

import requests

from tinybird.tb.client import AuthNoTokenException, TinyB
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.exceptions import CLIException

TB_IMAGE_NAME = "tinybirdco/tinybird-local:beta"
TB_CONTAINER_NAME = "tinybird-local"
TB_LOCAL_PORT = int(os.getenv("TB_LOCAL_PORT", 7181))
TB_LOCAL_HOST = f"http://localhost:{TB_LOCAL_PORT}"


async def get_tinybird_local_client(config_obj: Dict[str, Any], build: bool = False, staging: bool = False) -> TinyB:
    """Get a Tinybird client connected to the local environment."""

    config = await get_tinybird_local_config(config_obj, build=build)
    return config.get_client(host=TB_LOCAL_HOST, staging=staging)


async def get_tinybird_local_config(config_obj: Dict[str, Any], build: bool = False) -> CLIConfig:
    """Craft a client config with a workspace name based on the path of the project files

    It uses the tokens from tinybird local
    """
    path = config_obj.get("path")
    config = CLIConfig.get_project_config()

    try:
        # ruff: noqa: ASYNC210
        tokens = requests.get(f"{TB_LOCAL_HOST}/tokens").json()
    except Exception:
        raise CLIException("Tinybird local is not running. Please run `tb local start` first.")

    user_token = tokens["user_token"]
    admin_token = tokens["admin_token"]
    default_token = tokens["workspace_admin_token"]
    # Create a new workspace if path is provided. This is used to isolate the build in a different workspace.
    if path:
        user_client = config.get_client(host=TB_LOCAL_HOST, token=user_token)
        ws_name = get_build_workspace_name(path) if build else config.get("name") or config_obj.get("name")
        if not ws_name:
            raise AuthNoTokenException()

        logging.debug(f"Workspace used for build: {ws_name}")

        user_workspaces = requests.get(
            f"{TB_LOCAL_HOST}/v1/user/workspaces?with_organization=true&token={admin_token}"
        ).json()
        user_org_id = user_workspaces.get("organization_id", {})
        local_workspaces = user_workspaces.get("workspaces", [])

        ws = next((ws for ws in local_workspaces if ws["name"] == ws_name), None)

        if not ws:
            await user_client.create_workspace(
                ws_name, template=None, assign_to_organization_id=user_org_id, version="v1"
            )
            user_workspaces = requests.get(f"{TB_LOCAL_HOST}/v1/user/workspaces?token={admin_token}").json()
            ws = next((ws for ws in user_workspaces["workspaces"] if ws["name"] == ws_name), None)
            if not ws:
                raise AuthNoTokenException()

        ws_token = ws["token"]

        config.set_token(ws_token)
        config.set_token_for_host(TB_LOCAL_HOST, ws_token)
        config.set_host(TB_LOCAL_HOST)
    else:
        config.set_token(default_token)
        config.set_token_for_host(TB_LOCAL_HOST, default_token)

    config.set_user_token(user_token)
    return config


def get_build_workspace_name(path: str) -> str:
    folder_hash = hashlib.sha256(path.encode()).hexdigest()
    return f"Tinybird_Local_Build_{folder_hash}"
