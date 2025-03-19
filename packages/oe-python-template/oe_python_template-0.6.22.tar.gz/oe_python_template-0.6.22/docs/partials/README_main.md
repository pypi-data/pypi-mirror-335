Copier template to scaffold Python projects compliant with best practices and modern tooling.

Use Cases:
1) Fast and easy generation of Python projects from this template
2) Seamless updates of projects when improvements to the template are released
3) Generates a fully-functional Python package with test and build automation featuring
   - Service architecture suiteable for use as shared library
   - Command-line interface (CLI)
   - Versioned Web API
   - Integration examples with Notebooks and Dashboards
   - Complete developer-tooling with formatting, linting, type checking etc.
   - CI/CD pipeline for GitHub, PyPI, and Docker registries
   - Unit and E2E tests including parallel and matrix-testing
   - Release artifacts include SBOM, license information, and test coverage
   - Auto-generated documentation published to Read The Docs
   - Service integrations monitoring code quality, dependencies, and security

## Scaffolding

**Step 1**: Install uv package manager and copier
```shell
if [[ "$OSTYPE" == "darwin"* ]]; then                 # Install dependencies for macOS X
  if ! command -v brew &> /dev/null; then             ## Install Homebrew if not present
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then            # Install dependencies for Linux
  sudo apt-get update -y && sudo apt-get install curl -y # Install curl
fi
if ! command -v uvx &> /dev/null; then                # Install uv package manager if not present
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source $HOME/.local/bin/env
fi
uv tool install copier                                # Install copier as global tool
```

**Step 2**: Now create an empty repository on GitHub, clone to your local machine, and change into it's directory.

**Step 3**: Scaffold the project
```shell
copier copy --trust gh:helmut-hoffer-von-ankershoffen/oe-python-template .
```

**Step 4**: Perform initial commit and push
```shell
git add .
git commit -m "feat: Initial commit"
git push
```

Visit your GitHub repository and check the Actions tab. The CI workflow should fail at the SonarQube step,
as this external service is not yet configured for our new repository.

**Step 5**: Follow the [instructions](SERVICE_CONNECTIONS.md) to wire up
external services such as Cloudcov, SonarQube Cloud, Read The Docs, Docker.io, GHCR.io and Streamlit Community Cloud.

**Step 6**: Release the first versions
```shell
./n bump
```
Notes:
* You can remove this section post having successfully scafolded your project.
* The following sections refer to the dummy application and service provided by this template.
  Use them as inspiration and adapt them to your own project.

## Overview

Adding OE Python Template to your project as a dependency is easy. See below for usage examples.

```shell
uv add oe-python-template             # add dependency to your project
```

If you don't have uv installed follow [these instructions](https://docs.astral.sh/uv/getting-started/installation/). If you still prefer pip over the modern and fast package manager [uv](https://github.com/astral-sh/uv), you can install the library like this:


```shell
pip install oe-python-template        # add dependency to your project
```

Executing the command line interface (CLI) in an isolated Python environment is just as easy:

```shell
uvx oe-python-template hello-world       # prints "Hello, world! [..]"
uvx oe-python-template serve             # serves web API
uvx oe-python-template serve --port=4711 # serves web API on port 4711
```

Notes:
* The API is versioned, mounted at `/api/v1` resp. `/api/v2`
* While serving the web API go to [http://127.0.0.1:8000/api/v1/hello-world](http://127.0.0.1:8000/api/v1/hello-world) to see the respons of the `hello-world` operation.
* Interactive documentation is provided at [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)


The CLI provides extensive help:

```shell
uvx oe-python-template --help                # all CLI commands
uvx oe-python-template hello-world --help    # help for specific command
uvx oe-python-template echo --help
uvx oe-python-template openapi --help
uvx oe-python-template serve --help
```


## Operational Excellence

This project is designed with operational excellence in mind, using modern Python tooling and practices. It includes:

* Various examples demonstrating usage:
  - [Simple Python script](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/script.py)
  - [Streamlit web application](https://oe-python-template.streamlit.app/) deployed on [Streamlit Community Cloud](https://streamlit.io/cloud)
  - [Jupyter](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/notebook.ipynb) and [Marimo](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/notebook.py) notebook
* [Complete reference documentation](https://oe-python-template.readthedocs.io/en/latest/reference.html) on Read the Docs
* [Transparent test coverage](https://app.codecov.io/gh/helmut-hoffer-von-ankershoffen/oe-python-template) including unit and E2E tests (reported on Codecov)
* Matrix tested with [multiple python versions](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/noxfile.py) to ensure compatibility (powered by [Nox](https://nox.thea.codes/en/stable/))
* Compliant with modern linting and formatting standards (powered by [Ruff](https://github.com/astral-sh/ruff))
* Up-to-date dependencies (monitored by [Renovate](https://github.com/renovatebot/renovate) and [GitHub Dependabot](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/security/dependabot))
* [A-grade code quality](https://sonarcloud.io/summary/new_code?id=helmut-hoffer-von-ankershoffen_oe-python-template) in security, maintainability, and reliability with low technical debt and codesmell (verified by SonarQube)
* Additional code security checks using [GitHub CodeQL](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/security/code-scanning)
* [Security Policy](SECURITY.md)
* [License](LICENSE) compliant with the Open Source Initiative (OSI)
* 1-liner for installation and execution of command line interface (CLI) via [uv(x)](https://github.com/astral-sh/uv) or [Docker](https://hub.docker.com/r/helmuthva/oe-python-template/tags)
* Setup for developing inside a [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) included (supports VSCode and GitHub Codespaces)


## Usage Examples

The following examples run from source - clone this repository using
`git clone git@github.com:helmut-hoffer-von-ankershoffen/oe-python-template.git`.

### Minimal Python Script:

```python
"""Example script demonstrating the usage of the service provided by OE Python Template."""

from dotenv import load_dotenv
from rich.console import Console

from oe_python_template import Service

console = Console()

load_dotenv()

message = Service.get_hello_world()
console.print(f"[blue]{message}[/blue]")
```

[Show script code](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/script.py) - [Read the reference documentation](https://oe-python-template.readthedocs.io/en/latest/reference.html)

### Streamlit App

Serve the functionality provided by OE Python Template in the web by easily integrating the service into a Streamlit application.

[Try it out!](https://oe-python-template.streamlit.app) - [Show the code](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/streamlit.py)

... or serve the app locally
```shell
uv sync --all-extras                                # Install streamlit dependency part of the examples extra, see pyproject.toml
uv run streamlit run examples/streamlit.py          # Serve on localhost:8501, opens browser
```

## Notebooks

### Jupyter

[Show the Jupyter code](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/notebook.ipynb)

... or run within VSCode

```shell
uv sync --all-extras                                # Install dependencies required for examples such as Juypyter kernel, see pyproject.toml
```
Install the [Jupyter extension for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)

Click on `examples/notebook.ipynb` in VSCode and run it.

### Marimo

[Show the marimo code](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template/blob/main/examples/notebook.py)

Execute the notebook as a WASM based web app

```shell
uv sync --all-extras                                # Install ipykernel dependency part of the examples extra, see pyproject.toml
uv run marimo run examples/notebook.py --watch      # Serve on localhost:2718, opens browser
```

or edit interactively in your browser

```shell
uv sync --all-extras                                # Install ipykernel dependency part of the examples extra, see pyproject.toml
uv run marimo edit examples/notebook.py --watch     # Edit on localhost:2718, opens browser
```

... or edit interactively within VSCode

Install the [Marimo extension for VSCode](https://marketplace.visualstudio.com/items?itemName=marimo-team.vscode-marimo)

Click on `examples/notebook.py` in VSCode and click on the caret next to the Run icon above the code (looks like a pencil) > "Start in marimo editor" (edit).

## Command Line Interface (CLI)

### Run with [uvx](https://docs.astral.sh/uv/guides/tools/)

Show available commands:

```shell
uvx oe-python-template --help
```

Execute commands:

```shell
uvx oe-python-template hello-world
uvx oe-python-template echo --help
uvx oe-python-template echo "Lorem"
uvx oe-python-template echo "Lorem" --json
uvx oe-python-template openapi
uvx oe-python-template openapi --output-format=json
uvx oe-python-template serve
```

### Environment

The service loads environment variables including support for .env files.

```shell
cp .env.example .env              # copy example file
echo "THE_VAR=MY_VALUE" > .env    # overwrite with your values
```

Now run the usage examples again.

### Run with Docker

You can as well run the CLI within Docker.

```shell
docker run helmuthva/oe-python-template --help
docker run helmuthva/oe-python-template hello-world
docker run helmuthva/oe-python-template echo --help
docker run helmuthva/oe-python-template echo "Lorem"
docker run helmuthva/oe-python-template echo "Lorem" --json
docker run helmuthva/oe-python-template openapi
docker run helmuthva/oe-python-template openapi --output-format=json
docker run helmuthva/oe-python-template serve
```

Execute command:

```shell
docker run --env THE_VAR=MY_VALUE helmuthva/oe-python-template echo "Lorem Ipsum"
```

Or use docker compose

The .env is passed through from the host to the Docker container.

```shell
docker compose run oe-python-template --help
docker compose run oe-python-template hello-world
docker compose run oe-python-template echo --help
docker compose run oe-python-template echo "Lorem"
docker compose run oe-python-template echo "Lorem" --json
docker compose run oe-python-template openapi
docker compose run oe-python-template openapi --output-format=json
docker compose up
curl http://127.0.0.1:8000/api/v1/hello-world
curl http://127.0.0.1:8000/api/v1/docs
curl http://127.0.0.1:8000/api/v2/hello-world
curl http://127.0.0.1:8000/api/v2/docs
```

## Extra: Lorem Ipsum

Dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam.
