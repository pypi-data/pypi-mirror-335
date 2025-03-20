# FlowScript

FlowScript is a Python package that automates workflow scheduling and execution based on a JSON configuration and an SQLite database. It includes modules for parsing workflow configurations, scheduling tasks, executing tasks, and managing workflow execution.

## Features

- **Workflow Parsing:** Parse and validate workflow configurations from a JSON file.
- **Task Scheduling:** Manage and schedule tasks using an SQLite database.
- **Task Execution:** Execute tasks concurrently using threading.
- **Logging:** Integrated logging for tracking workflow progress and errors.
- **Modular Design:** Components such as parser, scheduler, task executor, and workflow engine are separated into distinct modules for easy maintenance and extension.

## Installation

After publishing on PyPI, you can install the package using:

```bash
pip install test_automation
