from typing import Optional

import rich_click as click
from grpc import RpcError

from union._config import _get_config_obj
from union.app import App
from union.cli._common import _get_channel_with_org
from union.cli._option import MutuallyExclusiveArgument, MutuallyExclusiveOption
from union.internal.secret.definition_pb2 import SecretIdentifier, SecretSpec
from union.internal.secret.payload_pb2 import UpdateSecretRequest
from union.internal.secret.secret_pb2_grpc import SecretServiceStub


@click.group(name="update")
def update():
    """Update a resource."""


@update.command()
@click.argument(
    "name",
    required=False,
    cls=MutuallyExclusiveArgument,
    mutually_exclusive=["name_option"],
    error_msg="Please pass --name once: `union update secret --name NAME`",
)
@click.option(
    "--name",
    "name_option",
    help="Secret name",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["name"],
    error_msg="Please pass --name once: `union update secret --name NAME`",
)
@click.option(
    "--value",
    help="Secret value",
    prompt="Enter secret value",
    hide_input=True,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["value_file"],
)
@click.option(
    "-f",
    "--value-file",
    help="Path to file containing the secret",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, allow_dash=True),
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["value"],
)
@click.option("--project", help="Project name")
@click.option("--domain", help="Domain name")
def secret(
    name: Optional[str],
    name_option: Optional[str],
    value: str,
    value_file: str,
    project: Optional[str],
    domain: Optional[str],
):
    """Update secret with NAME."""
    name = name or name_option

    platform_obj = _get_config_obj().platform
    channel, org = _get_channel_with_org(platform_obj)

    if value_file:
        with open(value_file, "rb") as f:
            secret_spec = SecretSpec(binary_value=f.read())
    else:
        secret_spec = SecretSpec(string_value=value)

    stub = SecretServiceStub(channel)
    request = UpdateSecretRequest(
        id=SecretIdentifier(name=name, domain=domain, project=project, organization=org),
        secret_spec=secret_spec,
    )

    try:
        stub.UpdateSecret(request)
        click.echo(f"Updated secret with name: {name}")
    except RpcError as e:
        raise click.ClickException(f"Unable to update secret with name: {name}\n{e}") from e


def update_application(app: App, project: str, domain: str):
    from union.configuration import UnionAIPlugin

    remote = UnionAIPlugin.get_remote(config=None, project=project, domain=domain)
    remote._app_remote.update(app)
