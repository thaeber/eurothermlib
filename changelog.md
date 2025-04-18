<!-- insertion marker -->

<a name="v0.1.4"></a>

## [v0.1.4](https://github.com/thaeber/eurothermlib/compare/v0.1.3...v0.1.4) (2025-04-18)

### Bug Fixes

- Roll over server log at midnight ([4282d37](https://github.com/thaeber/eurothermlib/commit/4282d37b14b2d22f89cff0df18600b06c2d6a7b5))

### Chore

- pre-commit (excluding proto generated files) ([785e5df](https://github.com/thaeber/eurothermlib/commit/785e5dffc5500fb7c384b7108d64f11bb0a1a3bc))

<a name="v0.1.3"></a>

## [v0.1.3](https://github.com/thaeber/eurothermlib/compare/v0.1.2...v0.1.3) (2025-03-05)

### Features

- Sending digital trigger signals in time or temperature intervals ([9168efd](https://github.com/thaeber/eurothermlib/commit/9168efdda6e7f6c054d729f6b3fd5086a8667ce9))

<a name="v0.1.2"></a>

## [v0.1.2](https://github.com/thaeber/eurothermlib/compare/v0.1.1...v0.1.2) (2025-01-22)

### Bug Fixes

- `strict` keyword argument in ModbusSerialClient removed ([2753eac](https://github.com/thaeber/eurothermlib/commit/2753eac43d8b2b59cb231585a99ec1aff7e61f49))

### Chore

- git-changelog -B patch ([25ab06a](https://github.com/thaeber/eurothermlib/commit/25ab06a05a294412252a10a1283b37dd8bc5d13b))
- pre-commit run --all ([d6dc7cc](https://github.com/thaeber/eurothermlib/commit/d6dc7cc5160c4d44ffd23b8a9bc24fd2713bc8e9))

<a name="v0.1.1"></a>

## [v0.1.1](https://github.com/thaeber/eurothermlib/compare/2a527035bf11a206a900e002170c4cbe36b50da1...v0.1.1) (2025-01-17)

### Bug Fixes

- added protobuf extra to grpcio to dependencies ([7813b8e](https://github.com/thaeber/eurothermlib/commit/7813b8eb8e2a6b5bb54e9a6dbd432aed0b355476))
- typo in log message ([b78fa38](https://github.com/thaeber/eurothermlib/commit/b78fa388c8ad4be7387a79c3584d8b5b2a5c647b))
- stop IO threads open server termination ([77d3c15](https://github.com/thaeber/eurothermlib/commit/77d3c154a60bd1e81fff986ec32c47eb7f245a95))

### Features

- single log file for each client command with timestamp ([451e56e](https://github.com/thaeber/eurothermlib/commit/451e56eb44bd374f06843b5374898a9ab859880d))
- hold command to wait for given time period ([69a4f20](https://github.com/thaeber/eurothermlib/commit/69a4f204ea04499e415c13e7d8af300502e94001))
- automatic logging of process temperature ([15cc1d3](https://github.com/thaeber/eurothermlib/commit/15cc1d303144396f40b7333b93a35b9c90dd9c76))
- split logging between server and client ([cb7cd62](https://github.com/thaeber/eurothermlib/commit/cb7cd62dded4dd35f4989ccb9d69776afa7bbb88))
- Added data logging configuration ([d910348](https://github.com/thaeber/eurothermlib/commit/d910348305c8740280765ba661b97fa9a23cafd7))
- show config CLI ([a24f900](https://github.com/thaeber/eurothermlib/commit/a24f9006b26ba5e68d3d7237e7750f290671cec9))
- set remote setpoint from textual UI ([50d2098](https://github.com/thaeber/eurothermlib/commit/50d2098e8e0d476eede62ced387188cf67e4232b))
- stopping remote ramp & ramp state in textual UI ([574ae7a](https://github.com/thaeber/eurothermlib/commit/574ae7ac6d40e489697f7d9ab22ed5c3f59d3264))
- server side stream of temperature ramp (#5) ([70a272b](https://github.com/thaeber/eurothermlib/commit/70a272b2970384cc6c4115434738ea5968894b78))
- basic implementation of temperature ramps ([8074686](https://github.com/thaeber/eurothermlib/commit/8074686e5a8727309ffa17307cc05c57824232a0))
- reconnect dialog in textual UI upon connection errors ([cd65238](https://github.com/thaeber/eurothermlib/commit/cd65238edbc57d0cf005ad81371f155a3f20642e))
- added remote setpoint to process values ([06860a0](https://github.com/thaeber/eurothermlib/commit/06860a0d8ca72b3cd25e780b55e59218b016ca92))
- enable/disable/set remote setpoint ([a92204e](https://github.com/thaeber/eurothermlib/commit/a92204ec1ab3d9d69a1d8e3622538b12ac3fe8d3))
- implement RPC call and CLI to reset alarms ([2833ebc](https://github.com/thaeber/eurothermlib/commit/2833ebc86c76c63a13536f5c6b1268babbad3412))
- Textual based command line UI (#4) ([acc7e34](https://github.com/thaeber/eurothermlib/commit/acc7e34835bf8bca9309a36377425deb75ab33f1))
- SerialModbus connection with synchronization (#3) ([47d186a](https://github.com/thaeber/eurothermlib/commit/47d186a616e2107592cdd7c46ee21624c015fd86))
- CLI for starting/stopping the server (#2) ([9323ff8](https://github.com/thaeber/eurothermlib/commit/9323ff8794331ee6d0a617fee2770aa15324977e))
- Stream current process values (#1) ([c0a7d96](https://github.com/thaeber/eurothermlib/commit/c0a7d9629498e3efa08995788c18e6e928c1ec2c))

### Code Refactoring

- data stream now uses aggreagted process values from controller ([dc10ffa](https://github.com/thaeber/eurothermlib/commit/dc10ffa7e5ae7af8f20f3debeef489b88e4e3c54))
- Moved controllers to sub folder and splitting classes into different files ([4fb8817](https://github.com/thaeber/eurothermlib/commit/4fb8817d2fa5e1a202d8b9257eaa14b1cefaf579))

### Chore

- updated changelog.md ([2223422](https://github.com/thaeber/eurothermlib/commit/22234227d9c1d0668d9ddfc55db3a7ad1632fac6))
- pre-commit run --all-files ([bfb9e84](https://github.com/thaeber/eurothermlib/commit/bfb9e847b78fb9dd32755d1c724413926d86e1dc))
- run pre-commit ([e4f89ed](https://github.com/thaeber/eurothermlib/commit/e4f89ed4ae8c4db9adb587f42ff330095ab68792))
- pre-commit (excluding proto generated files) ([5dad126](https://github.com/thaeber/eurothermlib/commit/5dad126abd6cea0efa8b74826338be86312ef244))
- Simulate PID controller ([6852cc7](https://github.com/thaeber/eurothermlib/commit/6852cc72a252471b5ece9af4834834e3b9450584))
- Basic gRPC server/client code. ([2824edd](https://github.com/thaeber/eurothermlib/commit/2824edda871e1235ab77bd5268b7f6f44e26dba4))
- Initial commit ([2a52703](https://github.com/thaeber/eurothermlib/commit/2a527035bf11a206a900e002170c4cbe36b50da1))

### Build

- **deps:** upgrading to python 3.11 ([1d97532](https://github.com/thaeber/eurothermlib/commit/1d97532f34a697726704dee69d1e9a33df5be30e))
