import importlib.util
import os
import sys
from copy import deepcopy
from functools import partial
from pathlib import Path
from textwrap import dedent
from typing import Dict

import rich_click as click

from union._config import _DEFAULT_DOMAIN, _DEFAULT_PROJECT_BYOC, _get_default_project
from union.app import App, Input


class ApplicationCommand(click.RichCommand):
    def __init__(
        self,
        app: App,
        project: str,
        domain: str,
        debug: bool,
        *args,
        **kwargs,
    ):
        self.app = app
        self.project = project
        self.domain = domain
        self.debug = debug

        kwargs["params"] = [
            click.Option(
                param_decls=[f"--{app_input.name}"],
                required=False,
                type=str,
                help=f"Set {app_input.name}",
            )
            for app_input in app.inputs
        ]

        super().__init__(*args, **kwargs)

    def invoke(self, ctx):
        app = self.app

        # Check if there are any dynamic inputs
        has_new_inputs = False
        new_inputs = []

        for user_input in app.inputs:
            key = user_input.name.lower()
            if key in ctx.params and ctx.params[key]:
                new_inputs.append(
                    Input(
                        name=user_input.name,
                        value=ctx.params[key],
                        download=user_input.download,
                    )
                )
                has_new_inputs = True
            else:
                new_inputs.append(user_input)

        if has_new_inputs:
            app = deepcopy(app)
            app.inputs = new_inputs

        if self.debug:
            app.command = [
                "sh",
                "-c",
                f"set -e; echo '🚀 Setting up vscode 🛠️'; curl -fsSL https://code-server.dev/install.sh | sh; "
                f"code-server --bind-addr 0.0.0.0:{app.port} --disable-workspace-trust --auth none;",
            ]

            app.args = []
            app.min_replicas = 1
            app.max_replicas = 1

        from union.configuration import UnionAIPlugin

        remote = UnionAIPlugin.get_remote(config=None, project=self.project, domain=self.domain)
        remote.deploy_app(app)


class ApplicationForFileGroup(click.RichGroup):
    def __init__(
        self,
        filename: Path,
        project: str,
        domain: str,
        debug: bool,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not filename.exists():
            raise click.ClickException(f"{filename} does not exists")
        self.filename = filename
        self.project = project
        self.domain = domain
        self.debug = debug

    @property
    def apps(self) -> Dict[str, App]:
        try:
            return self._apps
        except AttributeError:
            module_name = os.path.splitext(os.path.basename(self.filename))[0]
            module_path = os.path.dirname(os.path.abspath(self.filename))

            spec = importlib.util.spec_from_file_location(module_name, self.filename)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            sys.path.append(module_path)
            spec.loader.exec_module(module)

            from union.app._models import APP_REGISTRY

            app_directory = os.path.dirname(os.path.abspath(self.filename))
            cwd = os.getcwd()
            self._apps = {k: v._resolve_include(app_directory, cwd) for k, v in APP_REGISTRY.apps.items()}
            return self._apps

    def list_commands(self, ctx):
        return list(self.apps.keys())

    def get_command(self, ctx, app_name):
        try:
            return ApplicationCommand(
                app=self.apps[app_name],
                name=app_name,
                project=self.project,
                domain=self.domain,
                debug=self.debug,
            )
        except KeyError:
            valid_names = list(self.apps.keys())
            err_msg = dedent(f"""\
                '{app_name}' is not a valid app name in {self.filename}

                Valid names are: {valid_names}""")
            raise click.ClickException(err_msg)


class DeployApplicationGroupForFiles(click.RichGroup):
    def __init__(self, command_name: str, *args, **kwargs):
        kwargs["params"] = [
            click.Option(
                param_decls=["-p", "--project"],
                required=False,
                type=str,
                default=partial(_get_default_project, previous_default=_DEFAULT_PROJECT_BYOC),
                help=f"Project to run {command_name}",
                show_default=True,
            ),
            click.Option(
                param_decls=["-d", "--domain"],
                required=False,
                type=str,
                default=_DEFAULT_DOMAIN,
                help=f"Domain to run {command_name}",
                show_default=True,
            ),
            click.Option(
                param_decls=["-n", "--name"],
                required=False,
                type=str,
                help="Application name to start",
                show_default=True,
            ),
            click.Option(
                param_decls=["--debug"],
                required=False,
                type=bool,
                is_flag=True,
                default=False,
                help="Start app in debug mode (vscode server). It requires `sh` and `curl` to be available on the"
                " image. VSCode Server will be downloaded on demand.",
                show_default=True,
            ),
        ]
        super().__init__(*args, **kwargs)
        self.command_name = command_name

    @property
    def files(self):
        try:
            return self._files
        except AttributeError:
            self._files = [os.fspath(p) for p in Path(".").glob("*.py") if p.name != "__init__.py"]
            return self._files

    def invoke(self, ctx):
        if "name" in ctx.params and not ctx.protected_args:
            # Command is invoked with just `--name`
            project = ctx.params.get("project", _DEFAULT_PROJECT_BYOC)
            domain = ctx.params.get("domain", _DEFAULT_DOMAIN)
            name = ctx.params.get("name")

            from union.configuration import UnionAIPlugin

            remote = UnionAIPlugin.get_remote(config=None, project=project, domain=domain)
            remote._app_remote.start(name)
            return

        return super().invoke(ctx)

    def list_commands(self, ctx):
        return self.files

    def get_command(self, ctx, filename):
        return ApplicationForFileGroup(
            filename=Path(filename),
            name=filename,
            project=ctx.params.get("project", _DEFAULT_PROJECT_BYOC),
            domain=ctx.params.get("domain", _DEFAULT_DOMAIN),
            debug=ctx.params.get("debug", False),
            help=f"{self.command_name} application in {filename}",
        )
