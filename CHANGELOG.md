# Changelog

## [1.1.0](https://github.com/ZeroGachis/magicparse/compare/1.0.2...1.1.0) (2026-02-18)


### Features

* Expose a Transform class to build & evaluate a JSONata expression ([07b1fe3](https://github.com/ZeroGachis/magicparse/commit/07b1fe3d1e2e486ca2679178ae6b3d90b3d09e8c))


### Miscellaneous Chores

* **vscode:** Improve default settings ([d9869c5](https://github.com/ZeroGachis/magicparse/commit/d9869c50ec41a68cc793885fa861368605022366))


### Code Refactoring

* Rename internal 'Tranform' abstract class into 'ParsingTransform' ([830bff5](https://github.com/ZeroGachis/magicparse/commit/830bff5de4066f47934ed6a2d97be065eb76677a))

## [1.0.2](https://github.com/ZeroGachis/magicparse/compare/1.0.1...1.0.2) (2026-02-17)


### Miscellaneous Chores

* Move to Python 3.13 / Poetry 2.2 + Speedup CI builds ([2df0bcb](https://github.com/ZeroGachis/magicparse/commit/2df0bcbe5d0adfaf4551822dcb053eaed03fdb8e))

## [1.0.1](https://github.com/ZeroGachis/magicparse/compare/1.0.0...1.0.1) (2025-09-24)


### Miscellaneous Chores

* Replace black/flake8 with ruff ([2f3fab3](https://github.com/ZeroGachis/magicparse/commit/2f3fab3d9162ec3b9b2251ef11315e5926569868))
* Setup pre-commit ([12f6d7d](https://github.com/ZeroGachis/magicparse/commit/12f6d7d1138951089c5d3d23cb72c0968512a0fd))
* Setup pyright and expose type annotations ([a25273f](https://github.com/ZeroGachis/magicparse/commit/a25273f20a4fd521ac45fea9b03f7344e78cfb70))


### Continuous Integration

* add permissions on github actions ([265b87c](https://github.com/ZeroGachis/magicparse/commit/265b87c2c07f9a1454477970d229dfe0784fdf89))

## [1.0.0](https://github.com/ZeroGachis/magicparse/compare/0.16.1...1.0.0) (2025-09-19)


### ⚠ BREAKING CHANGES

* Add breaking changes

### Features

* Add coalesce computed field ([424d888](https://github.com/ZeroGachis/magicparse/commit/424d888189c406f316558b9af0216c24bb180a2c))
* Add error handling in Transformer ([bd5a0f9](https://github.com/ZeroGachis/magicparse/commit/bd5a0f99419811926a022c83969dbf998e54d044))
* add not-null-or-empty validator ([4d5ce0d](https://github.com/ZeroGachis/magicparse/commit/4d5ce0d9e8160eeeac56ef4709a4ae6227bdda8e))
* field type can be describe with complexe structure ([6b09fe7](https://github.com/ZeroGachis/magicparse/commit/6b09fe71f4ac2b2fa5a8ebce47da953287de850b))
* Implement nullable type ([39e85c5](https://github.com/ZeroGachis/magicparse/commit/39e85c5fd82c54834798ac06302452de224aed6b))
* Return type row to know if row is success, skip or in error ([773d7e5](https://github.com/ZeroGachis/magicparse/commit/773d7e5e4572ebc958fc8865d1b6e431325b7f18))


### Bug Fixes

* ComputedField can have access to previous computed field values ([436ca68](https://github.com/ZeroGachis/magicparse/commit/436ca68c2e361c62ce78408b9b69030c65bd7e2c))


### Documentation

* Add breaking changes ([0676ff6](https://github.com/ZeroGachis/magicparse/commit/0676ff617660744f26145d55a49ce9385ad6ee35))


### Miscellaneous Chores

* Remove missing step for mise test task ([1a7b94e](https://github.com/ZeroGachis/magicparse/commit/1a7b94e741d235e991757cea57552f0d18ed527e))
* Update README to match with current lib state ([afa9471](https://github.com/ZeroGachis/magicparse/commit/afa9471c87ea7596887fd5f6df37dd72379de1db))
* Use pytest to assert exception ([79ebf31](https://github.com/ZeroGachis/magicparse/commit/79ebf3104be2d31f3087bc494da237b8478d12c7))


### Code Refactoring

* Move out of transformer skiping logic ([54a8dfc](https://github.com/ZeroGachis/magicparse/commit/54a8dfcf3dc8504539c86e7d148417776c024c33))

## [0.16.1](https://github.com/ZeroGachis/magicparse/compare/0.16.0...0.16.1) (2025-09-15)


### Bug Fixes

* Do not alter dict given in args ([6b15f81](https://github.com/ZeroGachis/magicparse/commit/6b15f811c49aa73cf91cda5f9d1fb8456d112cf9))

## [0.16.0](https://github.com/ZeroGachis/magicparse/compare/0.15.0...0.16.0) (2025-09-15)


### Features

* add security scan workflow ([92a58c9](https://github.com/ZeroGachis/magicparse/commit/92a58c9705c9aa0b8cc6364c0537eabe7ea8ac85))
* improve error message ([5c7d817](https://github.com/ZeroGachis/magicparse/commit/5c7d81700e35cda3b5fa0d90024844072cb6af19))


### Bug Fixes

* add missing build method for computed field ([4121b28](https://github.com/ZeroGachis/magicparse/commit/4121b289f22927ba3882697f25df20f45ac9155d))


### Miscellaneous Chores

* Add .env ([c0d2b8f](https://github.com/ZeroGachis/magicparse/commit/c0d2b8fb781098117b1e29c1df56bc163b01babb))
* Add mise setup ([435e28a](https://github.com/ZeroGachis/magicparse/commit/435e28aef039d79ce8ab55ad042ebf8658d70fa5))
* Add vscode debug settings ([33ff3ba](https://github.com/ZeroGachis/magicparse/commit/33ff3baa1442292aadd77ecc72a7f805a7b15ee2))
* Bump python image ([744e916](https://github.com/ZeroGachis/magicparse/commit/744e916ae24902b8f710237087c99902f4e4d04e))
* **deps:** update dependency black to v25 ([f81c8f9](https://github.com/ZeroGachis/magicparse/commit/f81c8f9de0d2f8a6784c6ff5aaa4069e67ce0f49))
* **deps:** update dependency black to v25 ([7856cb1](https://github.com/ZeroGachis/magicparse/commit/7856cb14d8cfb8a71c32aebbafebc7bb02ff8d94))
* Update vscode settings ([f783f4f](https://github.com/ZeroGachis/magicparse/commit/f783f4f21ddbebd7d6ec8bd5428eee19dbc9c6b9))
* upgrade python from 3.11 to 3.12 ([af7f0f5](https://github.com/ZeroGachis/magicparse/commit/af7f0f5d004b5f87d2293350acc5bd97b331b103))

## [0.15.0](https://github.com/ZeroGachis/magicparse/compare/0.14.0...0.15.0) (2024-08-27)


### Features

* update to python 3.11 ([55a5fa4](https://github.com/ZeroGachis/magicparse/commit/55a5fa4f8c9d2df176eeaeeae6f0bb3e27eec0b4))


### Miscellaneous Chores

* add CODEOWNERS ([4962f29](https://github.com/ZeroGachis/magicparse/commit/4962f29abd40bda61d74fd972c66f801fc3051be))
* add service catalog for techportal ([78ca92d](https://github.com/ZeroGachis/magicparse/commit/78ca92d50f904b7220bd31863bfdbeb804ae44ee))
* **deps:** update black to 24 ([20e443e](https://github.com/ZeroGachis/magicparse/commit/20e443e6b458a9c39ba1154c7ba29b9f029ce15d))
* **deps:** update flake8 to 7 ([4e985f6](https://github.com/ZeroGachis/magicparse/commit/4e985f645ec1c0238cc546ef493cd54ced7aa999))
* **deps:** update poetry lock file ([fd4054e](https://github.com/ZeroGachis/magicparse/commit/fd4054e97baf3e1132a15d440f3925daaf5698aa))
* **deps:** update pytest to 8 ([f836e66](https://github.com/ZeroGachis/magicparse/commit/f836e66c985eb59ce9da455e749ee1eaaaef303c))
* switch to release please system ([2ade4c9](https://github.com/ZeroGachis/magicparse/commit/2ade4c9b9ef81d0509984a54135ed8807f52642f))


### Continuous Integration

* update pullrequest CI to last common workflows version ([72b4829](https://github.com/ZeroGachis/magicparse/commit/72b48292f1767f3891e8d88feb73a202f1f52c90))
* update release ci to use releaseplease ([01b8040](https://github.com/ZeroGachis/magicparse/commit/01b80407cbdf71a4bef70befb1fe939af6511ad0))
