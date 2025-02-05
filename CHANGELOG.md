# Changelog

## [1.5.7](https://github.com/yte-template-engine/yte/compare/v1.5.6...v1.5.7) (2025-02-05)


### Bug Fixes

* fix bug appearing with empty dicts ([#51](https://github.com/yte-template-engine/yte/issues/51)) ([33ab11f](https://github.com/yte-template-engine/yte/commit/33ab11f403736b775ad05b11b7f68e0ed667bd64))

## [1.5.6](https://github.com/yte-template-engine/yte/compare/v1.5.5...v1.5.6) (2025-01-20)


### Bug Fixes

* handle numpy strings in lists and dicts returned by expressions, auto-convert numpy ndarrays to equivalent lists ([#49](https://github.com/yte-template-engine/yte/issues/49)) ([7e648a1](https://github.com/yte-template-engine/yte/commit/7e648a107b435326b2aa19f70630834e95eb1b18))

## [1.5.5](https://github.com/yte-template-engine/yte/compare/v1.5.4...v1.5.5) (2024-12-09)


### Bug Fixes

* increase serialization robustness by explicitly converting numpy strings to python strings ([#47](https://github.com/yte-template-engine/yte/issues/47)) ([2640720](https://github.com/yte-template-engine/yte/commit/2640720a12069d773b3fbff04e0c967b9471a1ab))

## [1.5.4](https://github.com/yte-template-engine/yte/compare/v1.5.3...v1.5.4) (2023-12-11)


### Miscellaneous Chores

* fix release process ([7ed63f9](https://github.com/yte-template-engine/yte/commit/7ed63f9fde43899b4b1b746003d66d869a0ed415))

## [1.5.3](https://github.com/yte-template-engine/yte/compare/v1.5.2...v1.5.3) (2023-12-11)


### Miscellaneous Chores

* release 1.5.3 ([d3d9e56](https://github.com/yte-template-engine/yte/commit/d3d9e56cf40a53999b0e46a67c766e6a1d229b8e))

## [1.5.2](https://github.com/yte-template-engine/yte/compare/v1.5.1...v1.5.2) (2023-12-11)


### Bug Fixes

* fix errors occuring in document context building when having dicts as list items ([#37](https://github.com/yte-template-engine/yte/issues/37)) ([f347d32](https://github.com/yte-template-engine/yte/commit/f347d32845f4e0bd109adf3fde9e5e25d956c852))

## [1.5.1](https://github.com/yte-template-engine/yte/compare/v1.5.0...v1.5.1) (2022-06-03)


### Bug Fixes

* revert to Python 3.9 for release uploading ([a35a10c](https://github.com/yte-template-engine/yte/commit/a35a10c77cae661d9696e672e382cd8c1b20bc31))

## [1.5.0](https://github.com/yte-template-engine/yte/compare/v1.4.0...v1.5.0) (2022-06-03)


### Features

* allow to require a __use_yte__ statement when processing ([#27](https://github.com/yte-template-engine/yte/issues/27)) ([abf3d95](https://github.com/yte-template-engine/yte/commit/abf3d95c1a241088f24825606034e35c0600be7b))

## [1.4.0](https://www.github.com/yte-template-engine/yte/compare/v1.3.0...v1.4.0) (2022-05-10)


### Features

* rename the global doc object into `this` (`doc` remains available as an alias) ([#25](https://www.github.com/yte-template-engine/yte/issues/25)) ([e3adc67](https://www.github.com/yte-template-engine/yte/commit/e3adc67094188e5af8000580d4732e7d8fa68a09))


### Documentation

* CLI and formatting ([e21512d](https://www.github.com/yte-template-engine/yte/commit/e21512d1a71761f9078a6abf8ea2b4708fe5caf0))

## [1.3.0](https://www.github.com/yte-template-engine/yte/compare/v1.2.3...v1.3.0) (2022-05-09)


### Features

* enable access to already rendered parts of the document via a global variable `doc` ([#23](https://www.github.com/yte-template-engine/yte/issues/23)) ([a2ac30a](https://www.github.com/yte-template-engine/yte/commit/a2ac30a6c97124bc4a57405877832b48b1a8bb4f))
* variable definitions as an alternative to full Python definitions ([#19](https://www.github.com/yte-template-engine/yte/issues/19)) ([c1f4b1c](https://www.github.com/yte-template-engine/yte/commit/c1f4b1ceacd662db33c2e55968c9f402724adbe1))


### Documentation

* Fix README.md example ([#22](https://www.github.com/yte-template-engine/yte/issues/22)) ([0247fe2](https://www.github.com/yte-template-engine/yte/commit/0247fe229a6c38940f485bcce18f51a6dea72551))

### [1.2.3](https://www.github.com/yte-template-engine/yte/compare/v1.2.2...v1.2.3) (2022-05-06)


### Bug Fixes

* display error context ([#17](https://www.github.com/yte-template-engine/yte/issues/17)) ([cbe74a3](https://www.github.com/yte-template-engine/yte/commit/cbe74a357be3449bbb8e0325f1e87ec6469a4b3b))


### Documentation

* add example and testcase for variable definition ([#15](https://www.github.com/yte-template-engine/yte/issues/15)) ([818f886](https://www.github.com/yte-template-engine/yte/commit/818f886b9c44f2bd15fe5e0f32119c0c3ace3ca1))

### [1.2.2](https://www.github.com/yte-template-engine/yte/compare/v1.2.1...v1.2.2) (2022-04-12)


### Documentation

* fix readme example and better error message in case of mixing list and dict returns ([#13](https://www.github.com/yte-template-engine/yte/issues/13)) ([afc0e69](https://www.github.com/yte-template-engine/yte/commit/afc0e69b0ab5a9c2087558886336f34227fd248b))

### [1.2.1](https://www.github.com/yte-template-engine/yte/compare/v1.2.0...v1.2.1) (2022-03-18)


### Bug Fixes

* improved error message in case of YAML syntax errors ([#11](https://www.github.com/yte-template-engine/yte/issues/11)) ([4377e22](https://www.github.com/yte-template-engine/yte/commit/4377e22566edbff34083687256fb269b95ee788b))


### Documentation

* Fix example for __definitions__ ([#9](https://www.github.com/yte-template-engine/yte/issues/9)) ([4fff096](https://www.github.com/yte-template-engine/yte/commit/4fff096109b5e3ed5141e4294232c20aaf2bdd1f))

## [1.2.0](https://www.github.com/yte-template-engine/yte/compare/v1.1.0...v1.2.0) (2022-02-28)


### Features

* rename __imports__ into __definitions__ reflecting that it actually allows arbitrary Python statements ([35dde8f](https://www.github.com/yte-template-engine/yte/commit/35dde8f7cb9c8a71d9006f116972ed89d3795535))

## [1.1.0](https://www.github.com/yte-template-engine/yte/compare/v1.0.0...v1.1.0) (2022-02-28)


### Features

* allow import statements via special keyword __imports__ ([be4e497](https://www.github.com/yte-template-engine/yte/commit/be4e497d952747169db1418f288f2025a1654153))


### Documentation

* import keyword ([4582037](https://www.github.com/yte-template-engine/yte/commit/45820379337d5b98e3a70290e9488d11cd3022af))

## [1.0.0](https://www.github.com/yte-template-engine/yte/compare/v0.2.0...v1.0.0) (2022-02-21)

first stable language release

## [0.2.0](https://www.github.com/yte-template-engine/yte/compare/v0.1.1...v0.2.0) (2022-02-18)


### Features

* python 3.7 support ([#4](https://www.github.com/yte-template-engine/yte/issues/4)) ([fcd69e2](https://www.github.com/yte-template-engine/yte/commit/fcd69e28e8af53789f04015e89e64fab03bf1701))

### [0.1.1](https://www.github.com/yte-template-engine/yte/compare/v0.1.0...v0.1.1) (2022-02-15)


### Bug Fixes

* more relaxed Python version dependency, more metadata ([#2](https://www.github.com/yte-template-engine/yte/issues/2)) ([545275f](https://www.github.com/yte-template-engine/yte/commit/545275ff90071c400b06ae7512db530dafb197a9))

## 0.1.0 (2022-02-15)


### Features

* add command line interface ([688ab12](https://www.github.com/yte-template-engine/yte/commit/688ab124268b3a9f9191f66d5486d5196493c2c0))


### Documentation

* API documentation ([d0931d5](https://www.github.com/yte-template-engine/yte/commit/d0931d54804ff9527cd2b663d40585586961fd5b))
