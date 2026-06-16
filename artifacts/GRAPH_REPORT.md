# GRAPH_REPORT — Graphify

- Nodes: **459**  ·  Edges: **398**  ·  Communities: **139**  ·  Bridges: **250**

## God-node / bottleneck candidates (highest betweenness)
_All paths through one node = architectural risk; verify against source._

- `generate_files` — betweenness 0.006 (`cookiecutter/generate.py::generate_files`)
- `cookiecutter` — betweenness 0.006 (`cookiecutter/main.py::cookiecutter`)
- `determine_repo_dir` — betweenness 0.002 (`cookiecutter/repository.py::determine_repo_dir`)
- `_run_hook_from_repo_dir` — betweenness 0.002 (`cookiecutter/generate.py::_run_hook_from_repo_dir`)
- `run_hook` — betweenness 0.002 (`cookiecutter/hooks.py::run_hook`)

## Top central nodes (degree)

- `generate_files` — degree 0.097
- `cookiecutter` — degree 0.064
- `cli_runner` — degree 0.046
- `prompt_for_config` — degree 0.042
- `unzip` — degree 0.040
- `cookiecutter.exceptions` — degree 0.038
- `determine_repo_dir` — degree 0.038
- `CookiecutterException` — degree 0.035

## Bridges (single points of dependency)

- `cookiecutter.cli` — `cookiecutter.log`
- `version_msg` — `main`
- `main` — `cookiecutter`
- `main` — `configure_logger`
- `_expand_path` — `get_config`
- `merge_configs` — `get_config`
- `merge_configs` — `test_merge_configs`
- `get_config` — `test_get_config`
- `get_config` — `test_get_config_does_not_exist`
- `get_config` — `test_invalid_config`
- `get_config` — `test_get_config_with_defaults`
- `get_user_config` — `test_get_user_config_valid`
- `get_user_config` — `test_get_user_config_invalid`
- `get_user_config` — `test_get_user_config_nonexistent`
- `get_user_config` — `test_specify_config_path`
