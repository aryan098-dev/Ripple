# 🌊 Ripple — Change Impact Intelligence Platform

**Understand the impact of code changes. Find relevant tests. Validate with confidence.**

Ripple is a developer intelligence platform that analyzes code changes, maps dependencies, identifies potentially affected modules, and recommends relevant tests to help developers validate changes more efficiently.

It currently supports Python and JavaScript projects through a unified analysis engine and an interactive Streamlit dashboard.

---

## 🚀 Key Features

- **Git Change Detection:** Identifies modified, added, deleted, and renamed files in a Git repository.
- **Multi-Language Analysis:** Supports Python and JavaScript through a modular adapter architecture.
- **Dependency Graph:** Builds relationships between project modules using extracted imports.
- **Impact Analysis:** Identifies directly and indirectly affected modules.
- **Intelligent Test Recommendations:** Uses test imports and filename matching to identify potentially relevant tests.
- **Automated Test Execution:** Runs recommended Python tests with pytest and JavaScript tests with Vitest.
- **Interactive Dashboard:** Presents change analysis, dependency impact, test recommendations, and execution results in a Streamlit interface.
- **Target Repository Selection:** Allows users to analyze a selected local Git repository.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Core engine | Python |
| Dashboard | Streamlit |
| Python analysis | AST |
| JavaScript analysis | Regex-based parsing |
| Version control | Git |
| Python testing | pytest |
| JavaScript testing | Vitest |

## 🏗️ Architecture

Ripple follows a modular architecture:

```text
                    ┌─────────────────────┐
                    │   Target Git Repo   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Git Change        │
                    │   Detection         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Language Adapters  │
                    │  Python / JavaScript│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Dependency Graph    │
                    │ Construction        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Impact Analysis     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Test Recommendation │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Automated Test      │
                    │ Execution           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └─────────────────────┘
```

### Analysis Workflow

1. Ripple detects changes in the selected Git repository.
2. Language adapters extract imports and symbols from supported files.
3. The dependency graph maps relationships between modules.
4. Impact analysis identifies potentially affected modules.
5. The test recommender matches discovered tests against changed and impacted modules.
6. The test runner executes the recommended tests.
7. Results are presented in the interactive dashboard.

## 📂 Project Structure

```text
Ripple/
│
├── dashboard.py
├── requirements.txt
├── package.json
├── package-lock.json
├── README.md
├── LICENSE
│
├── ripple/
│   ├── __init__.py
│   ├── engine.py
│   ├── ast_analyzer.py
│   ├── git_diff.py
│   ├── dependency_graph.py
│   ├── impact_analyzer.py
│   ├── test_recommender.py
│   ├── test_runner.py
│   │
│   └── adapters/
│       ├── __init__.py
│       ├── base.py
│       ├── registry.py
│       ├── python_adapter.py
│       └── javascript_adapter.py
│
└── sample_project/
    ├── payment.py
    ├── checkout.py
    ├── calculator.js
    ├── app.js
    ├── app.test.js
    └── tests/
        └── test_checkout.py
```

## ⚙️ Installation

### Prerequisites

Make sure you have installed:

- Python 3.12 or compatible Python version
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/aryan098-dev/Ripple.git
cd Ripple
```

### 2. Create a Python virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install JavaScript dependencies

```bash
npm ci
```

This installs the JavaScript development dependencies, including Vitest.

## ▶️ Running Ripple

Start the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

Open the local URL displayed in your terminal.

### Analyze a repository

1. Open the Ripple dashboard.
2. Find the **Target Repository** field in the sidebar.
3. Enter the absolute path to a local Git repository.
4. Click **Run Ripple Analysis**.
5. Explore the Overview, Impact Analysis, and Test Recommendations pages.

**Important:** The target must be an accessible Git repository. Ripple analyzes Git changes relative to the repository's current baseline. A clean repository may produce zero changed files.

## 🧪 Running Tests

### Python tests

```bash
python -m pytest
```

### JavaScript tests

```bash
npm test
```

### Sample project

The `sample_project/` directory contains example Python and JavaScript files and tests that can be used to explore Ripple's analysis workflow.

To see meaningful change detection, make a small modification to a tracked source file in a Git repository before running Ripple.

## 🔍 Test Recommendation Method

Ripple currently uses two forms of matching evidence:

| Method | Description |
|---|---|
| Import-based matching | Checks whether a test directly imports a changed or impacted module. |
| Filename-based matching | Uses naming relationships between source modules and test files as a fallback. |

Import-based matches receive high priority, while filename-based matches receive medium priority.

**Note:** These recommendations indicate potential test relevance. They do not guarantee code coverage or prove that every affected behavior is tested.

## 🌐 Current Language Support

| Language | Dependency extraction | Symbol extraction | Test execution |
|---|---|---|---|
| Python | Supported | Supported | pytest |
| JavaScript | Supported | Supported | Vitest |

The current JavaScript analyzer uses lightweight regular-expression-based parsing rather than a complete JavaScript parser.

## ⚠️ Current Limitations

Ripple is an evolving developer tool. Some limitations of the current implementation include:

- Static dependency analysis cannot detect every dynamic dependency.
- JavaScript parsing is lightweight and does not cover every language construct.
- Test recommendations use import and filename relationships rather than measured code coverage.
- Dependency resolution may not understand every custom alias or package configuration.
- Test execution runs commands on the local machine and is not sandboxed.

**Security:** Only analyze repositories and execute tests from sources you trust. Test code can execute commands on your machine.

## 🗺️ Future Scope

Potential future improvements include:

- More programming language adapters.
- Deeper static analysis and dependency resolution.
- Coverage-aware test recommendations.
- Improved visualization of dependency relationships.
- CI/CD integration.
- More advanced change-risk analysis.

These are future directions, not claims about currently implemented functionality.

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the relevant tests.
5. Submit a pull request describing your changes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👨‍💻 Project

**Ripple — Change Impact Intelligence Platform**

GitHub: https://github.com/aryan098-dev/Ripple

Built to help developers understand code changes and validate them with greater confidence.
