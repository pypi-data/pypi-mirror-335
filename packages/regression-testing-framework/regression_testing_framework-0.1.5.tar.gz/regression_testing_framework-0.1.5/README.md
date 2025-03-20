# Regression Testing Framework

A framework for running parallel test configurations with log discovery and summary reports.

## Features

- Run multiple test configurations in parallel
- Automatic log collection and failure detection
- Summary reports for test runs
- Built with pure Python - no external services required

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
   base_command: /bin/bash
   successful_run:
     params:
       - { c: "echo 'This command will succeed'" }
   failing_run:
     params:
       - { c: "exit 1" }
   another_successful_run:
     params:
       - { c: "echo 'Another successful command'" }
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
3. Results are collected and a summary report is generated

## License

This project is licensed under the terms of the LICENSE file included in the repository.