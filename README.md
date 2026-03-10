# snowstream-cli
**version:** 0.0.0a (Alpha)

___
**Snowstream CLI** is a lightweight command-line toolkit for bootstrapping and working with Snowstream projects.

It provides:

- A project **scaffolding / init** command to create a standard Snowstream directory layout.
- A **manifest generator** that produces a `snowstream_manifest.json` file from a project definition.
- A **build runner** that validates a project and generates the manifest for a target app/environment.

---

## ✅ Requirements

- **Python** 3.11 (supports `>=3.11,<3.12`)
- **pip** (recommended latest stable, e.g., 25.x)

---

## 🚀 Installation

Install via `pip`:

```bash
pip install snowstream-cli
```

If you are developing locally, install in editable mode from the repo root:

```bash
pip install -e .
```

---

## 🧰 CLI Usage

The package exposes a console script named `snowstream` (configured via `pyproject.toml`).

### Initialize a new project

Creates a `snowstream/` project layout in the current directory (or a provided path).

```bash
snowstream init
```

**Options:**

- `--project-dir PATH` : Target directory (default: current working directory)
- `--force` : Overwrite an existing Snowstream project directory without prompting

### Generate a manifest

Produces a `snowstream_manifest.json` file in the project directory (under `.manifest/`).

```bash
snowstream manifest
```

**Options:**

- `--project-dir PATH` : Path to the Snowstream project directory (default: current working directory)
- `--app NAME` : Target app to include (default: all apps)

### Run a build

Validates the project and generates the manifest for a given environment.

```bash
snowstream run
```

**Options:**

- `--project-dir PATH` : Path to the Snowstream project directory (default: current working directory)
- `--app NAME` : Target app to run (default: all apps)
- `--target {dev,test,prod}` : Build target environment (default: dev)

---

## 📁 Project Structure (Scaffold)

When you run `snowstream init`, the following structure is created:

```
./
  .gitignore
  .locals/
    profile.yml
  .manifest/
  snowstream/
    project.yml
    apps/
```

Key files and folders:

- `.locals/profile.yml` : Local environment settings (account, user, role, etc.)
- `.manifest/` : Where generated manifests are written
- `snowstream/project.yml` : Core project definition used by the manifest generator
- `snowstream/apps/` : Optional app-specific configuration

---

## 🔧 Development

To run tests and linting from the repo root:

```bash
pytest
pylint snowstream_cli
```

---

## 📦 Dependencies

Key runtime dependencies (see `pyproject.toml`):

- `snowflake-cli`, `snowflake-snowpark-python`, `snowflake-connector-python`
- `PyYAML`, `toml`
- `streamlit` (for any UI/streaming helpers)

---

## 📝 Notes

- The CLI and core logic are implemented under `src/snowstream_cli/`.
- Templates used for scaffolding live under `src/snowstream_cli/templates/`.

---

## 🪪 License

This project is published under the terms of the **Apache 2.0 License** (see `LICENSE`).


##  Related Projects
**snowstream-library**
```
pip install snowstream-lib
```
**snowstream-framework**
```
pip install snowstream-framework
```
