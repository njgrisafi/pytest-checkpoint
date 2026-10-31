# Changelog

All notable changes to `pytest-checkpoint` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.3] - 2026-10-31

### Changed
- Packaging now uses the uv build backend and requires uv >=0.13.6,<0.14
- Development tools updated to mypy 2.4.1 and ruff 0.17.3

### Security
- GitHub Actions updated to current Node 24 releases
- CI Python versions pinned to 3.11.18, 3.12.16, and 3.13.18

## [0.1.3] - 2025-10-03

### Fixed
-  comparison overlap type errors

## [0.1.2] - 2025-03-29

### Fixed
- pytest version range is now >=8.0.0

## [0.1.1] - 2025-03-22

### Fixed
- logo loading on pypi
- github artifact

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
