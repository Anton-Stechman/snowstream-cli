import os
import json
from typing import Generator
import yaml
from snowstream_cli._utilities._backend import dir_exists, get_file, MessageType

def generate_snowstream_manifest(project_path: str, target_app: str | None = None) -> Generator:
    """
    Generate a Snowstream manifest for one or all apps in the project.

    ### Inputs
        - project_path `<type=str>`: Path to the snowstream project directory.
        - target_app (optional) `<type=str | None>` <default=`None`>: Target app to build manifest for. If `None` or `"all"`, all apps are included.

    ### Returns
        `Generator`: Yields `tuple[str, MessageType]` pairs for each build step, with the final yield being the manifest `dict`.

    ### Raises
        None
    """
    apps_root: str = os.path.join(project_path, "apps")
    manifest: dict = {"apps": []}

    def __parse_app(app_path: str, app_name: str) -> Generator:
        app_yml_path: str = os.path.join(app_path, "app.yml")
        if not os.path.isfile(app_yml_path):
            yield f"Warning: no app.yml found for app '{app_name}' at {app_yml_path}", MessageType.WARNING
            return

        app_config: dict = get_file(app_yml_path, parser=yaml.safe_load, internal=False)
        manifest_template: dict = get_file("templates", "files", "app.manifest.template", parser=json.loads)

        app_meta: dict = {}
        errors: list[str] = []

        for field, rules in manifest_template.items():
            required: bool = rules.get("required", False)
            default = rules.get("default")

            if field in app_config:
                app_meta[field] = app_config[field]
            elif required:
                errors.append(field)
            else:
                app_meta[field] = default

        if errors:
            for error in errors:
                yield f"ERROR: Missing required field '{error}' in app.yml for app '{app_name}'", MessageType.ERROR
            return

        manifest["apps"].append(app_meta)
        yield f"  [app] {app_name} loaded", MessageType.SUCCESS

    if target_app and target_app != "all":
        app_path: str = os.path.join(apps_root, target_app)
        if not dir_exists(app_path):
            yield f"App '{target_app}' not located at path {app_path}", MessageType.ERROR
            return
        yield from __parse_app(app_path, target_app)
    else:
        if not dir_exists(apps_root):
            yield f"Apps directory not found at {apps_root}", MessageType.ERROR
            return
        app_dirs: list[str] = [
            d for d in os.listdir(apps_root)
            if os.path.isdir(os.path.join(apps_root, d))
        ]
        if not app_dirs:
            yield f"No apps found in {apps_root}", MessageType.WARNING
            return
        for app_name in app_dirs:
            app_path: str = os.path.join(apps_root, app_name)
            yield from __parse_app(app_path, app_name)

    yield manifest, MessageType.SUCCESS
