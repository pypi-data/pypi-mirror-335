# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release with support for IPFS URIs in transformers and llama-cpp-python
- Automatic patching of from_pretrained methods
- Support for downloading models from IPFS
- Integration with HuggingFace Hub for llama-cpp models
- GitHub Actions for automated testing and PyPI deployment
- Comprehensive test suite with coverage reporting

### Changed

- Improved project structure with proper module organization
- Enhanced error handling and validation
- Better type hints and documentation

### Fixed

- IPFS URI handling in transformers and llama-cpp integrations
- Method patching to preserve original functionality

## [0.1.0] - 2025-03-21

### Added

- Initial project setup
- Basic IPFS integration
- Support for transformers and llama-cpp-python
- Documentation and examples
