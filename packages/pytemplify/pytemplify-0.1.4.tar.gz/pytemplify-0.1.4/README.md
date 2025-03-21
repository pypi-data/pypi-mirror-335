# pytemplify
Text file generator framework using parsed dictionary data and Jinja2 templates.

## How to create your generator using `pytemplify`
Install poetry:
```shell
curl -sSL https://install.python-poetry.org | python3 -
```
Install `pytemplify`:
```shell
pip install pytemplify
```
Generate the first skeleton of your generator using `mygen-init`:
```shell
cd <your-repo-path>
mygen-init
```
Complete the `TODO`s in modules; main implementation module is `parser_<your-generator-name>.py`.

Try to run:
```shell
poetry install
poetry run <your-generator-name>
```
```shell
poetry run nox
```

## TIPs
Activate poetry virtual environment:
```shell
source $(poetry env info --path)/bin/activate
```
Deactivate poetry virtual environment:
```shell
deactivate
```