# Changelog

All notable changes to `pytest-checkpoint` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-03-21

### Added
- Initial release of pytest-checkpoint
- Automatic test progress checkpointing
- Support for restoring test state after interruptions
- Two collection behaviors:
  - `deselect`: Remove previously passed tests from the collection
  - `skip`: Mark previously passed tests as skipped
- Configurable checkpoint file location via `--lap-out` option
- Support for handling expected failures and xfail tests
- Debug logging for checkpoint operations
- Compatible with Python 3.11+
