# Project Structure: filebundler
## Directory Structure
```
filebundler/
├── 📁 .cursor/
│   └── 📁 rules/
│       ├── 📄 app-flow-user.md
│       ├── 📄 app-flow.md
│       ├── 📄 core-features.md
│       ├── 📄 general.md
│       ├── 📄 overview.md
│       ├── 📄 prd.md
│       └── 📄 testing.md
├── 📁 .filebundler/
│   ├── 📁 bundles/
│   │   ├── 📄 bundle-management.json
│   │   ├── 📄 bundles-and-exports.json
│   │   ├── 📄 publish-pypi-setup.json
│   │   ├── 📄 settings-and-persistence.json
│   │   └── 📄 testing-ui-and-state.json
│   ├── 📄 project-structure.md
│   ├── 📄 selections.json
│   └── 📄 settings.json
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 python-publish.yml
├── 📁 .logfire/
│   └── 📄 .gitignore
├── 📁 .streamlit/
│   └── 📄 config.toml
├── 📁 dist/
│   ├── 📄 .gitignore
│   └── 📄 file_bundler-0.9.3.tar.gz
├── 📁 docs/
│   ├── 📄 ci-cd.md
│   ├── 📄 state-logic.md
│   ├── 📄 streamlit-testing-synthesized.md
│   └── 📄 test-suite.md
├── 📁 scripts/
│   ├── 📄 increase_version.py
│   └── 📄 start-server.bat
├── 📁 src/
│   ├── 📁 filebundler/
│   │   ├── 📁 lib/
│   │   │   └── 📁 llm/
│   │   │       ├── 📄 auto_bundle.py
│   │   │       ├── 📄 claude.py
│   │   │       └── 📄 utils.py
│   │   ├── 📁 managers/
│   │   │   ├── 📄 BundleManager.py
│   │   │   ├── 📄 GlobalSettingsManager.py
│   │   │   ├── 📄 ProjectSettingsManager.py
│   │   │   └── 📄 SelectionsManager.py
│   │   ├── 📁 models/
│   │   │   ├── 📁 llm/
│   │   │   │   └── 📄 AutoBundleResponse.py
│   │   │   ├── 📄 AppProtocol.py
│   │   │   ├── 📄 Bundle.py
│   │   │   ├── 📄 BundleMetadata.py
│   │   │   ├── 📄 FileItem.py
│   │   │   ├── 📄 GlobalSettings.py
│   │   │   └── 📄 ProjectSettings.py
│   │   ├── 📁 services/
│   │   │   ├── 📄 code_export_service.py
│   │   │   ├── 📄 project_structure.py
│   │   │   └── 📄 token_count.py
│   │   ├── 📁 ui/
│   │   │   ├── 📁 components/
│   │   │   │   └── 📄 selectable_file_items.py
│   │   │   ├── 📁 sidebar/
│   │   │   │   ├── 📄 file_tree.py
│   │   │   │   ├── 📄 file_tree_buttons.py
│   │   │   │   ├── 📄 project_selection.py
│   │   │   │   └── 📄 settings_panel.py
│   │   │   ├── 📁 tabs/
│   │   │   │   ├── 📁 auto_bundler/
│   │   │   │   │   ├── 📄 before_submit.py
│   │   │   │   │   └── 📄 render_auto_bundler.py
│   │   │   │   ├── 📄 debug.py
│   │   │   │   ├── 📄 export_contents.py
│   │   │   │   ├── 📄 global_settings_panel.py
│   │   │   │   ├── 📄 manage_bundles.py
│   │   │   │   └── 📄 selected_files.py
│   │   │   ├── 📄 confirm.py
│   │   │   └── 📄 notification.py
│   │   ├── 📁 utils/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 filepath_checker.py
│   │   │   ├── 📄 language_formatting.py
│   │   │   └── 📄 project_utils.py
│   │   ├── 📄 constants.py
│   │   ├── 📄 FileBundlerApp.py
│   │   └── 📄 state.py
│   ├── 📄 app.py
│   └── 📄 main.py
├── 📁 tests/
│   └── 📁 llm/
│       └── 📄 test_auto_bundle.py
├── 📄 .env
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 .pre-commit-config.yaml
├── 📄 .python-version
├── 📄 LICENSE
├── 📄 mypy.ini
├── 📄 pyproject.toml
├── 📄 README.md
├── 📄 test-utils.ipynb
├── 📄 TODO-further-out.md
└── 📄 TODO.md
```
