# pytest-checkpoint

<img src="https://raw.githubusercontent.com/njgrisafi/pytest-checkpoint/refs/heads/main/docs/logo.png" alt="pytest-checkpoint Logo" width="250" />

## Overview

`pytest-checkpoint` is a plugin for the [pytest](https://docs.pytest.org/en/stable/) testing framework that allows developers to restore their testing state from a checkpoint. This feature is particularly useful for long-running test suites, enabling you to pick up where you left off without having to rerun all tests.

### Perfect for Interruptible Environments

Running long test suites can be challenging when your environment isn't guaranteed to be stable. For example:
- Your CI pipeline might time out
- Your development machine might need a reboot
- Your cloud instance might be interrupted (i.e. AWS Spot instances)

`pytest-checkpoint` automatically saves your test progress, so you can pick up exactly where you left off when the system comes back online. This saves valuable time and computing resources, especially in environments where interruptions are common.

## Features

- **Checkpoint Restoration**: Automatically restore the state of tests from a previously saved checkpoint.
- **Flexible Collection Behavior**: Choose how tests are collected when restoring from a checkpoint (deselect or skip).
- **Detailed Logging**: Get insights into the checkpointing process with debug logs.

## Installation

You can install `pytest-checkpoint` using pip:

```bash
pip install pytest-checkpoint
```

## Usage

To use `pytest-checkpoint`, you need to add options to your pytest configuration. You can do this by adding the following lines to your `pytest.ini` or directly in the command line:

```ini
[pytest]
lap_out = .pytest_checkpoint/lap.json
collect_behavior = deselect  # or skip
```

### Command Line Options

- `--lap-out`: Specify the output file to store lap information for recording a checkpoint. Default is `.pytest_checkpoint/lap.json`.
- `--collect-behavior`: Determines how tests are collected when a checkpoint is restored. Options are `deselect` or `skip`.

### Example

Run your tests as usual, and the plugin will handle the checkpointing automatically:

```bash
pytest
```

If a test fails or is skipped, the plugin will mark it accordingly in the checkpoint file.

## Contributing

We welcome contributions from the community! To contribute to `pytest-checkpoint`, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch to your forked repository.
5. Create a pull request describing your changes.

## License

`pytest-checkpoint` is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Authors

- **Nick Grisafi** - [njgrisafi@gmail.com](mailto:njgrisafi@gmail.com)

## Acknowledgments

- Thanks to the [pytest](https://docs.pytest.org/en/stable/) community for their support and contributions to the testing ecosystem.

---

For more information, please refer to the [documentation](https://docs.pytest.org/en/stable/) or check the source code in this repository.
