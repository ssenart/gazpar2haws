# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-07-22

### Changed

[#77](https://github.com/ssenart/gazpar2haws/issues/77): Upgrade PyGazpar library version to 1.3.1.

## [0.3.2] - 2025-03-28

### Fixed

[#70](https://github.com/ssenart/gazpar2haws/issues/70): Remove as_of_date configuration property in default configuration template file.

## [0.3.1] - 2025-03-03

### Fixed

[#64](https://github.com/ssenart/gazpar2haws/issues/64): Data is always retrieved up to the application start date instead of up to now.

## [0.3.0] - 2025-02-15

### Added

[#31](https://github.com/ssenart/gazpar2haws/issues/31): Cost integration.

### Changed

[#60](https://github.com/ssenart/gazpar2haws/issues/60): Upgrade PyGazpar library version to 1.3.0.

## [0.2.1] - 2025-01-24

### Fixed

[#57](https://github.com/ssenart/gazpar2haws/issues/57): The addon configuration is the wrong format (still the old one).

## [0.2.0] - 2025-01-23

### Changed

[#55](https://github.com/ssenart/gazpar2haws/issues/55): Change HA addon configuration format to match gazpar2haws file configuration format.

## [0.1.14] - 2025-01-17

### Fixed

[#50](https://github.com/ssenart/gazpar2haws/issues/50): In dockerhub, version displayed in log file is wrong and always N-1.

## [0.1.13] - 2025-01-16

### Fixed

[#47](https://github.com/ssenart/gazpar2haws/issues/47): 'reset' configuration parameter is ignored in the addon configuration panel.

## [0.1.12] - 2025-01-15

### Fixed

[#37](https://github.com/ssenart/gazpar2haws/issues/37): Error GrDF send missing data with type="Absence de Données".

[#38](https://github.com/ssenart/gazpar2haws/issues/38): Using the HA addon, the PCE identifier is transformed into another number.

[#36](https://github.com/ssenart/gazpar2haws/issues/36): Error if HA endpoint configuration is missing in configuration.yaml.

### Added

[#33](https://github.com/ssenart/gazpar2haws/issues/33): Dockerhub 'latest' tag is currently published only if the release is created in the main branch.

## [0.1.11] - 2025-01-12

### Fixed

[#32](https://github.com/ssenart/gazpar2haws/issues/32): Fix fatal happening after introducing as_of_date for tests.

## [0.1.10] - 2025-01-11

### Fixed

[#28](https://github.com/ssenart/gazpar2haws/issues/28): Fix the code lint warning messages.

### Added

[#27](https://github.com/ssenart/gazpar2haws/issues/27): In a Github workflow, run unit tests against a HA container.

## [0.1.9] - 2025-01-10

### Fixed

[#26](https://github.com/ssenart/gazpar2haws/issues/26): Fix broken HA addons update.

## [0.1.8] - 2025-01-10

### Added

[#20](https://github.com/ssenart/gazpar2haws/issues/20): Automate build, package, publish with Github Actions.

## [0.1.7] - 2025-01-05

### Fixed

[#18](https://github.com/ssenart/gazpar2haws/issues/18): Regression on DockerHub deployment.

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
