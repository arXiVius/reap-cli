# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-06-23

### Added
- **Lightweight Identity Layer**: Added discoverable, minimal CLI credits via `--version` and `--about` flags. 
- **Graceful Terminal Degradation**: Robust `utf-8` and `cp1252` encoding fallback on Windows consoles for seamless display on legacy terminals.
- **First-Run Experience**: Helpful usage hints display when executing `reap` without arguments.

### Fixed
- **Async Asset Coroutine Bug**: Addressed a critical dependency locking bug in `engine.py` where downloaded assets were not correctly awaited in `queue_asset`.
- **Worker Loop Stability**: Handled unbounded `task_type` exceptions in the queue worker to prevent crash cascades on failing assets.
- **Test Integrity**: Rewrote the testing suite (`test_reap.py`) to align with the active `v2.0` architecture, covering domain matching, URL parsing, and path generation.
- **Dependency Isolation**: Added `venv/` and `.venv/` to `.gitignore`.

### Changed
- Standardized package architecture in `pyproject.toml` targeting `reap-cli` name.
- Upgraded default Python version requirements and metadata classifiers in `pyproject.toml`.

## [2.0.0] - Major Rewrite
### Added
- **Native Async Python Crawler**: Deprecated all `wget` dependencies in favor of a fast, native `aiohttp` graph crawler.
- **Playwright JS Snapshots**: Support for emulating complex JavaScript applications locally.
- **Offline Link Rewriting**: Deep path re-routing across all scraped HTML strings ensuring flawless local navigation.
- **Single File Bundling**: Embedded `base64` image conversions for singular `.html` exports.
