# Regression Testing Framework

A framework for running parallel test configurations with log discovery and summary reports.

## Features

- Run multiple test configurations in parallel
- Automatic log collection and failure detection
- Summary reports for test runs
- Built with pure Python - no external services required
- Configurable timeouts for long-running tests
- Improved process handling for reliable test completion

## Installation

```bash
pip install regression-testing-framework
```

Or install from source:

```bash
git clone https://github.com/username/regression_testing_framework.git
cd regression_testing_framework
pip install -e .
```

## Prerequisites

- Python 3.9+

## Quick Start

1. **Create Test Configuration**

   Create a YAML file (`config.yaml`) to define your tests:

   ```yaml
   # Global base command (optional, can be overridden by individual tests)
   base_command: /bin/bash

   # Simple test using base command
   successful_run:
     base_command: /bin/bash
     params:
       - -c
       - "echo 'This command will succeed'"

   # Python script execution test
   python_test:
     base_command: python
     params:
       - "-c"
       - "import os; print('Hello from Python')"
     environment:
       - DEBUG=true

   # Test with timeout for long-running processes
   long_running_test:
     base_command: python3
     params:
       - "-c"
       - "import time; print('Starting long task...'); time.sleep(10); print('Task completed')"
     timeout: 15  # Timeout in seconds
   ```

2. **Run Tests**

   Execute your tests:

   ```bash
   reggie run -i config.yaml -o test_report.txt
   ```

   For a dry run (to see what commands will be executed without running them):

   ```bash
   reggie run -i config.yaml --dry-run
   ```

   Control the number of parallel test executions:

   ```bash
   reggie run -i config.yaml -p 8  # Run 8 tests in parallel
   ```

## How It Works

1. The framework parses your YAML configuration file
2. Each test is executed in parallel using Python's ThreadPoolExecutor
3. Commands are executed directly without shell wrapping for improved reliability
4. Long-running tests can be configured with timeouts to prevent hanging
5. Results are collected and a summary report is generated

## Configuration Options

### Test Configuration

Each test in your YAML file can have the following properties:

- `base_command`: The executable to run (e.g., `python3`, `/bin/bash`)
- `params`: List of parameters to pass to the command
- `environment`: List of environment variables to set for the test
- `timeout`: Maximum time in seconds before the test is terminated (optional)

### Example Configuration

```yaml
my_test:
  base_command: python3
  params:
    - script.py
    - --arg1=value1
    - --arg2=value2
  environment:
    - ENV_VAR1=value1
    - ENV_VAR2=value2
  timeout: 300  # 5 minutes timeout
```

## License

This project is licensed under the terms of the LICENSE file included in the repository.