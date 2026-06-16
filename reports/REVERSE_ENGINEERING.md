# Reverse-Engineering Report (EX04 §5.2)

> Block diagram + OOP schema derived FROM THE GRAPH, plus insights.

## 1. Block / component architecture
```mermaid
flowchart TD
  subgraph (root)
    n___main___py["__main__.py"]
  end
  subgraph cookiecutter
    n_cookiecutter___init___py["__init__.py"]
    n_cookiecutter___main___py["__main__.py"]
    n_cookiecutter_cli_py["cli.py"]
    n_cookiecutter_config_py["config.py"]
    n_cookiecutter_environment_py["environment.py"]
    n_cookiecutter_exceptions_py["exceptions.py"]
    n_cookiecutter_extensions_py["extensions.py"]
    n_cookiecutter_find_py["find.py"]
    n_cookiecutter_generate_py["generate.py"]
    n_cookiecutter_hooks_py["hooks.py"]
    n_cookiecutter_log_py["log.py"]
    n_cookiecutter_main_py["main.py"]
    n_cookiecutter_prompt_py["prompt.py"]
    n_cookiecutter_replay_py["replay.py"]
    n_cookiecutter_repository_py["repository.py"]
    n_cookiecutter_utils_py["utils.py"]
    n_cookiecutter_vcs_py["vcs.py"]
    n_cookiecutter_zipfile_py["zipfile.py"]
  end
  subgraph tests
    n_tests___init___py["__init__.py"]
    n_tests_replay_test_dump_py["test_dump.py"]
    n_tests_replay_test_load_py["test_load.py"]
    n_tests_replay_test_replay_py["test_replay.py"]
    n_tests_repository_test_abbreviation_expansion_py["test_abbreviation_expansion.py"]
    n_tests_repository_test_determine_repo_dir_clones_repo_py["test_determine_repo_dir_clones_repo.py"]
    n_tests_repository_test_determine_repo_dir_finds_existing_cookiecutter_py["test_determine_repo_dir_finds_existing_cookiecutter.py"]
    n_tests_repository_test_determine_repo_dir_finds_subdirectories_py["test_determine_repo_dir_finds_subdirectories.py"]
    n_tests_repository_test_determine_repository_should_use_local_repo_py["test_determine_repository_should_use_local_repo.py"]
    n_tests_repository_test_is_repo_url_py["test_is_repo_url.py"]
    n_tests_repository_test_repository_has_cookiecutter_json_py["test_repository_has_cookiecutter_json.py"]
    n_tests_test_extensions_custom_extension_post_hooks_post_gen_project_py["post_gen_project.py"]
    n_tests_test_extensions_custom_extension_pre_hooks_pre_gen_project_py["pre_gen_project.py"]
    n_tests_test_extensions_hello_extension___init___py["__init__.py"]
    n_tests_test_extensions_hello_extension_hello_extension_py["hello_extension.py"]
    n_tests_test_generate_files_line_end_{{cookiecutter_test_name}}_{{cookiecutter_folder_name}}_{{cookiecutter_filename}}_py["{{cookiecutter.filename}}.py"]
    n_tests_test_output_folder_{{cookiecutter_test_name}}_{{cookiecutter_folder_name}}_{{cookiecutter_filename}}_py["{{cookiecutter.filename}}.py"]
    n_tests_test_pyhooks_hooks_post_gen_project_py["post_gen_project.py"]
    n_tests_test_pyhooks_hooks_pre_gen_project_py["pre_gen_project.py"]
    n_tests_test_pyshellhooks_hooks_post_gen_project_py["post_gen_project.py"]
    n_tests_test_pyshellhooks_hooks_pre_gen_project_py["pre_gen_project.py"]
    n_tests_test_abort_generate_on_hook_error_py["test_abort_generate_on_hook_error.py"]
    n_tests_test_cli_py["test_cli.py"]
    n_tests_test_cookiecutter_invocation_py["test_cookiecutter_invocation.py"]
    n_tests_test_cookiecutter_local_no_input_py["test_cookiecutter_local_no_input.py"]
    n_tests_test_cookiecutter_local_with_input_py["test_cookiecutter_local_with_input.py"]
    n_tests_test_custom_extensions_in_hooks_py["test_custom_extensions_in_hooks.py"]
    n_tests_test_default_extensions_py["test_default_extensions.py"]
    n_tests_test_environment_py["test_environment.py"]
    n_tests_test_exceptions_py["test_exceptions.py"]
    n_tests_test_find_py["test_find.py"]
    n_tests_test_generate_context_py["test_generate_context.py"]
    n_tests_test_generate_copy_without_render_py["test_generate_copy_without_render.py"]
    n_tests_test_generate_file_py["test_generate_file.py"]
    n_tests_test_generate_files_py["test_generate_files.py"]
    n_tests_test_generate_hooks_py["test_generate_hooks.py"]
    n_tests_test_get_config_py["test_get_config.py"]
    n_tests_test_get_user_config_py["test_get_user_config.py"]
    n_tests_test_hooks_py["test_hooks.py"]
    n_tests_test_log_py["test_log.py"]
    n_tests_test_main_py["test_main.py"]
    n_tests_test_output_folder_py["test_output_folder.py"]
    n_tests_test_preferred_encoding_py["test_preferred_encoding.py"]
    n_tests_test_prompt_py["test_prompt.py"]
    n_tests_test_read_repo_password_py["test_read_repo_password.py"]
    n_tests_test_read_user_choice_py["test_read_user_choice.py"]
    n_tests_test_read_user_dict_py["test_read_user_dict.py"]
    n_tests_test_read_user_variable_py["test_read_user_variable.py"]
    n_tests_test_read_user_yes_no_py["test_read_user_yes_no.py"]
    n_tests_test_repo_not_found_py["test_repo_not_found.py"]
    n_tests_test_specify_output_dir_py["test_specify_output_dir.py"]
    n_tests_test_utils_py["test_utils.py"]
    n_tests_undefined_variable_dir_name_{{cookiecutter_project_slug}}_{{cookiecutter_foobar}}_helloworld_py["helloworld.py"]
    n_tests_vcs_test_clone_py["test_clone.py"]
    n_tests_vcs_test_identify_repo_py["test_identify_repo.py"]
    n_tests_vcs_test_is_vcs_installed_py["test_is_vcs_installed.py"]
    n_tests_zipfile_test_unzip_py["test_unzip.py"]
  end
  n_cookiecutter___main___py --> n_cookiecutter_cli_py
  n_cookiecutter_cli_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_cli_py --> n_cookiecutter_log_py
  n_cookiecutter_cli_py --> n_cookiecutter_main_py
  n_cookiecutter_config_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_environment_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_find_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_generate_py --> n_cookiecutter_environment_py
  n_cookiecutter_generate_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_generate_py --> n_cookiecutter_find_py
  n_cookiecutter_generate_py --> n_cookiecutter_hooks_py
  n_cookiecutter_generate_py --> n_cookiecutter_utils_py
  n_cookiecutter_hooks_py --> n_cookiecutter_environment_py
  n_cookiecutter_hooks_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_main_py --> n_cookiecutter_config_py
  n_cookiecutter_main_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_main_py --> n_cookiecutter_generate_py
  n_cookiecutter_main_py --> n_cookiecutter_prompt_py
  n_cookiecutter_main_py --> n_cookiecutter_replay_py
  n_cookiecutter_main_py --> n_cookiecutter_repository_py
  n_cookiecutter_main_py --> n_cookiecutter_utils_py
  n_cookiecutter_prompt_py --> n_cookiecutter_environment_py
  n_cookiecutter_prompt_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_replay_py --> n_cookiecutter_utils_py
  n_cookiecutter_repository_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_repository_py --> n_cookiecutter_vcs_py
  n_cookiecutter_repository_py --> n_cookiecutter_zipfile_py
  n_cookiecutter_utils_py --> n_cookiecutter_prompt_py
  n_cookiecutter_vcs_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_vcs_py --> n_cookiecutter_utils_py
  n_cookiecutter_zipfile_py --> n_cookiecutter_exceptions_py
  n_cookiecutter_zipfile_py --> n_cookiecutter_prompt_py
  n_cookiecutter_zipfile_py --> n_cookiecutter_utils_py
  n_tests_repository_test_abbreviation_expansion_py --> n_cookiecutter_config_py
  n_tests_repository_test_abbreviation_expansion_py --> n_cookiecutter_repository_py
  n_tests_repository_test_is_repo_url_py --> n_cookiecutter_config_py
  n_tests_repository_test_is_repo_url_py --> n_cookiecutter_repository_py
  n_tests_repository_test_repository_has_cookiecutter_json_py --> n_cookiecutter_repository_py
  n_tests_test_cli_py --> n_cookiecutter___main___py
  n_tests_test_cli_py --> n_cookiecutter_main_py
  n_tests_test_default_extensions_py --> n_cookiecutter_main_py
  n_tests_test_environment_py --> n_cookiecutter_environment_py
  n_tests_test_environment_py --> n_cookiecutter_exceptions_py
  n_tests_test_generate_context_py --> n_cookiecutter_exceptions_py
  n_tests_test_generate_file_py --> n_cookiecutter_environment_py
  n_tests_test_generate_hooks_py --> n_cookiecutter_exceptions_py
  n_tests_test_get_config_py --> n_cookiecutter_exceptions_py
  n_tests_test_get_user_config_py --> n_cookiecutter_exceptions_py
  n_tests_test_log_py --> n_cookiecutter_log_py
  n_tests_test_main_py --> n_cookiecutter_main_py
  n_tests_test_read_repo_password_py --> n_cookiecutter_prompt_py
  n_tests_test_read_user_choice_py --> n_cookiecutter_prompt_py
  n_tests_test_read_user_dict_py --> n_cookiecutter_prompt_py
  n_tests_test_read_user_variable_py --> n_cookiecutter_prompt_py
  n_tests_test_read_user_yes_no_py --> n_cookiecutter_prompt_py
  n_tests_zipfile_test_unzip_py --> n_cookiecutter_exceptions_py
```

## 2. OOP class schema
```mermaid
classDiagram
  class ConfigDoesNotExistException
  class ContextDecodingException
  class CookiecutterException
  class ExtensionLoaderMixin
  class FailedHookException
  class HelloExtension
  class InvalidConfiguration
  class InvalidModeException
  class InvalidZipRepository
  class JsonifyExtension
  class MissingProjectDir
  class NonTemplatedInputDirException
  class OutputDirExistsException
  class RandomStringExtension
  class RepositoryCloneFailed
  class RepositoryNotFound
  class SlugifyExtension
  class StrictEnvironment
  class TestExternalHooks
  class TestFindHooks
  class TestPrompt
  class TestPromptChoiceForConfig
  class TestReadUserChoice
  class TestRenderVariable
  class UndefinedVariableInTemplate
  class UnknownExtension
  class UnknownRepoType
  class UnknownTemplateDirException
  class VCSNotInstalled
  ExtensionLoaderMixin <|-- StrictEnvironment
  CookiecutterException <|-- NonTemplatedInputDirException
  CookiecutterException <|-- UnknownTemplateDirException
  CookiecutterException <|-- MissingProjectDir
  CookiecutterException <|-- ConfigDoesNotExistException
  CookiecutterException <|-- InvalidConfiguration
  CookiecutterException <|-- UnknownRepoType
  CookiecutterException <|-- VCSNotInstalled
  CookiecutterException <|-- ContextDecodingException
  CookiecutterException <|-- OutputDirExistsException
  CookiecutterException <|-- InvalidModeException
  CookiecutterException <|-- FailedHookException
  CookiecutterException <|-- UndefinedVariableInTemplate
  CookiecutterException <|-- UnknownExtension
  CookiecutterException <|-- RepositoryNotFound
  CookiecutterException <|-- RepositoryCloneFailed
  CookiecutterException <|-- InvalidZipRepository
```

## 3. Architectural insights

### Insight A — God-node / bottleneck candidate
`cookiecutter` has the highest betweenness (0.006) — most paths route through it (`cookiecutter/main.py::cookiecutter`). The graph *suggests* a bottleneck; verify against source.

### Insight B — Rationale-vs-implementation gap
`cookiecutter/hooks.py::find_hook` — the docstring promises *"a dict of all hook scripts"*, but the buggy implementation `return`s the **first** matching path. The graph shows `run_hook --calls--> find_hook` (EXTRACTED) and `test_find_hook --tested_by--> find_hook`; the contract of the *called* function is the suspect. This docs-vs-code gap is the EX04 §4 architecture surprise.
