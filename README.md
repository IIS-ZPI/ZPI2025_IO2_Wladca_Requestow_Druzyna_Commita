# Currency Analytics System (CAS)

Currency Analytics System (CAS) is a command-line application (CLI) written in Python designed to perform statistical analysis and calculations on currency exchange rates based on data from the official National Bank of Poland (NBP) API. The system provides real-time statistical analysis including session patterns, statistical measures, and distribution analysis of currency exchange rates.

## Technology Stack

- **Language**: Python 3.10+
- **Core Libraries**: 
  - `requests` (2.31.0): HTTP library for API communication
  - `statistics`: Standard library for statistical calculations
  - `csv`: Standard library for CSV file handling
- **Testing Framework**: `pytest` (8.1.1) with automated unit testing
- **Data Source**: Official National Bank of Poland (NBP) REST API (public, no authentication required)
- **Development Environment**: Python virtual environment with isolated dependencies

## Running the Application

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Internet connection for NBP API access

### Installation and Execution

1. Navigate to the project directory:
   ```bash
   cd cas_project
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the CLI application:
   ```bash
   python main.py
   ```

### Application Menu
The CLI application provides the following analysis options:
- **Session Analysis**: Analyze currency rate movements (rising, falling, unchanged sessions)
- **Statistical Measures**: Calculate median, mode, standard deviation, and coefficient of variation
- **Distribution of Changes**: Analyze rate distribution patterns across predefined ranges
- **CSV Export**: Export analysis results to CSV files for external processing

### Deployment Environment

The application can be deployed on:
- **Local Development**: Windows, macOS, Linux machines
- **Server Deployment**: Linux servers with Python 3.10+ runtime
- **Containerized**: Docker containers with Python base image
- **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions

## Project Documentation

All comprehensive project documentation is located in the **`cas_project/docs/`** folder and includes:

- **Architecture.md**: Complete system architecture description with UML diagrams
  - Component diagram showing module interactions
  - Sequence diagram illustrating data flow
  - Activity diagram depicting user workflows
  - System design patterns and architectural decisions

- **BACKLOG.md**: Product backlog, user stories, and requirements prioritization
  - Link to Jira project for real-time tracking
  - Story points and sprint planning information

## Testing and Quality Assurance

### Test Structure
- **Unit Tests**: Located in `cas_project/test/` directory
  - `test_api.py`: API integration and data parsing validation
  - `test_analysis.py`: Statistical calculation verification
  - `test_export.py`: CSV export functionality testing
  - `test_main.py`: CLI interface and workflow testing

### Test Reports
Detailed test execution reports are available in **`cas_project/test/test_reports/`** directory:
- `test_api.md`: API module test coverage and results
- `test_analysis.md`: Analysis engine test coverage and results
- `test_export.md`: Export module test coverage and results
- `test_main.md`: Main CLI module test coverage and results

### Running Tests Locally

Execute all unit tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests with coverage report:
```bash
pytest --cov=cas_project
```

## Continuous Integration and Automation

### CI/CD Pipeline Implementation

The project uses **GitHub Actions** for automated testing and validation. The workflow is configured in `.github/workflows/`:

**Workflow: `test.yml`**
- **Trigger**: Automatic execution on every push to main branch and pull requests
- **Test Environment**: Python 3.10+ on Ubuntu latest
- **Steps**:
  1. Checkout source code
  2. Setup Python environment
  3. Install dependencies
  4. Execute all unit tests with pytest
  5. Generate test reports
  6. Perform code quality checks

**Benefits**:
- Immediate feedback on code changes
- Automated detection of regressions
- Consistent testing across all commits
- Prevention of broken code in main branch
- Compliance validation with project requirements

### Manual Test Execution
```bash
# Run complete test suite
pytest

# Run specific test file
pytest cas_project/test/test_api.py

# Run tests for specific function
pytest cas_project/test/test_api.py::test_pre_flight_input_fuzzing -v
```

## Project Structure

```
ZPI2025_IO2_Wladca_Requestow_Druzyna_Commita/
├── README.md                          # Project overview and setup instructions
├── pytest.ini                         # Pytest configuration
├── cas_project/
│   ├── main.py                        # CLI interface and application entry point
│   ├── api.py                         # NBP API integration module
│   ├── analysis.py                    # Statistical analysis engine
│   ├── export.py                      # CSV export utility
│   ├── models.py                      # Data model definitions
│   ├── requirements.txt               # Python dependency specifications
│   ├── docs/
│   │   ├── Architecture.md            # System architecture and UML diagrams
│   │   └── BACKLOG.md                 # Project backlog and requirements
│   └── test/
│       ├── test_api.py                # API module unit tests
│       ├── test_analysis.py           # Analysis module unit tests
│       ├── test_export.py             # Export module unit tests
│       ├── test_main.py               # Main CLI module unit tests
│       └── test_reports/
│           ├── test_api.md            # API test report
│           ├── test_analysis.md       # Analysis test report
│           ├── test_export.md         # Export test report
│           └── test_main.md           # Main module test report
└── .github/
    └── workflows/
        └── test.yml                   # GitHub Actions CI/CD workflow
```

## Backlog and Issue Tracking

**Primary Backlog**: [Jira Project Board](https://cas-project-wladca-requestow-druzyna-commita.atlassian.net/jira/software/projects/WRDC)

The Jira project contains:
- User stories and requirements
- Sprint planning and task allocation
- Issue tracking and resolution status
- Acceptance criteria and completion definition

**Secondary Backlog**: See `cas_project/docs/BACKLOG.md` for local backlog reference

## Development and Contribution Guidelines

- All code comments and documentation must be in English
- Follow PEP 8 Python style guide
- Write unit tests for new functionality
- Ensure all tests pass before committing
- Update documentation for any feature changes
- Use meaningful commit messages

## Support and Contact

For questions or issues regarding the Currency Analytics System project, please refer to:
1. Project documentation in `cas_project/docs/`
2. Jira project board for issue tracking
3. Test reports for troubleshooting information
