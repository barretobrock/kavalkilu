# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

_Note: 'Unreleased' section below is used for untagged changes that will be issued with the next version bump_

### [Unreleased] - 2022-00-00
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
__BEGIN-CHANGELOG__
 
### [2.1.1] - 2023-07-24
#### Changed
 - Made Home Assistant endpoint more flexible in terms of updating sensor states
 
### [2.1.0] - 2023-06-18
#### Added
 - Python 3.11 support
#### Changed
 - Makefile for dev support

### [2.0.3] - 2022-11-21
#### Added
 - Makefile
#### Changed
 - Server name for net api calls

### [2.0.2] - 2022-08-20
#### Added
 - pre-commit
 - exceptionhook and decorator to influx class

### [2.0.1] - 2022-04-24
#### Changed
 - The method for handling error logging to influx for automated notifications was moved to `InfluxDBLocal` class
#### Deprecated
 - Old logging objects - influx logging will need to be done separate

### [2.0.0] - 2022-04-20
#### Added
 - CHANGELOG
 - New structure for maintaining package

__END-CHANGELOG__
