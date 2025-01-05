# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2025-01-05

### Added

[#4](https://github.com/ssenart/gazpar2haws/issues/4): Deploy gazpar2haws as an HA add-on.

## [0.1.5] - 2025-01-04

### Added

[#15](https://github.com/ssenart/gazpar2haws/issues/15): Using HassIO, websocket endpoint is /core/websocket.

## [0.1.4] - 2025-01-04

### Fixed

[#13](https://github.com/ssenart/gazpar2haws/issues/13): Using HassIO, connection to the supervisor requires Authorization header.

## [0.1.3] - 2025-01-03

### Changed

[#11](https://github.com/ssenart/gazpar2haws/issues/11): Upgrade PyGazpar version to 1.2.6.

## [0.1.2] - 2024-12-30

### Added

[#2](https://github.com/ssenart/gazpar2haws/issues/2): DockerHub deployment.

### Fixed

[#9](https://github.com/ssenart/gazpar2haws/issues/9): Incorrect timezone info creates duplicate import.

[#6](https://github.com/ssenart/gazpar2haws/issues/6): The last meter value may be imported multiple times and cause the today value being wrong.

[#3](https://github.com/ssenart/gazpar2haws/issues/3): reset=false makes the meter import to restart from zero.

## [0.1.1] - 2024-12-22

### Added

[#1](https://github.com/ssenart/gazpar2haws/issues/1): Publish energy indicator in kWh.

## [0.1.0] - 2024-12-21

First version of the project.
