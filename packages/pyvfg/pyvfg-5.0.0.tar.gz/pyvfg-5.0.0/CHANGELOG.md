# Changelog

## [5.0.0](https://github.com/VersesTech/gpil/compare/pyvfg-v4.1.0...pyvfg-v5.0.0) (2025-03-21)


### ⚠ BREAKING CHANGES

* GPIL-401 VFG 0.5.0 (rebased) ([#288](https://github.com/VersesTech/gpil/issues/288))

### Features

* GPIL-401 VFG 0.5.0 (rebased) ([#288](https://github.com/VersesTech/gpil/issues/288)) ([f9f5476](https://github.com/VersesTech/gpil/commit/f9f5476e4f23604d71f9182e04e38a652cfc22e7))

## [4.1.0](https://github.com/VersesTech/gpil/compare/pyvfg-v4.0.0...pyvfg-v4.1.0) (2025-03-21)


### Features

* GPIL-409 MVP of MAP ([#281](https://github.com/VersesTech/gpil/issues/281)) ([458f1ab](https://github.com/VersesTech/gpil/commit/458f1abf56636b4f2c54c303e68cb674ef1cf9ab))

## [4.0.0](https://github.com/VersesTech/gpil/compare/pyvfg-v3.3.1...pyvfg-v4.0.0) (2025-03-21)


### ⚠ BREAKING CHANGES

* GPIL-491 learning overhaul; continuous learning by default ([#278](https://github.com/VersesTech/gpil/issues/278))

### Bug Fixes

* GPIL-491 learning overhaul; continuous learning by default ([#278](https://github.com/VersesTech/gpil/issues/278)) ([144af75](https://github.com/VersesTech/gpil/commit/144af7548b9652fdfa532bb056020d6bb9c38564))

## [3.3.1](https://github.com/VersesTech/gpil/compare/pyvfg-v3.3.0...pyvfg-v3.3.1) (2025-03-07)


### Bug Fixes

* GPIL-0 Typo correction ([#276](https://github.com/VersesTech/gpil/issues/276)) ([1def65e](https://github.com/VersesTech/gpil/commit/1def65e265bbaabe013766e4432c07e071e512ff))

## [3.3.0](https://github.com/VersesTech/gpil/compare/pyvfg-v3.2.0...pyvfg-v3.3.0) (2025-03-06)


### Features

* GPIL-343 rebase from SSoT; fixed latent var learning; optimized; new tests ([#259](https://github.com/VersesTech/gpil/issues/259)) ([851130f](https://github.com/VersesTech/gpil/commit/851130f317130e9ae6ad22bd3752fa4515e0f51b))


### Bug Fixes

* GPIL-0 pyvfg now lists all of its pyproject.toml dependencies ([#272](https://github.com/VersesTech/gpil/issues/272)) ([b29313a](https://github.com/VersesTech/gpil/commit/b29313af245ede45429205492e67b5e6030a0173))
* vfg_upgrade should convert a 030 vfg to 040 ([851130f](https://github.com/VersesTech/gpil/commit/851130f317130e9ae6ad22bd3752fa4515e0f51b))

## [3.2.0](https://github.com/VersesTech/gpil/compare/pyvfg-v3.1.2...pyvfg-v3.2.0) (2025-03-04)


### Features

* GPIL-382 Additional BDD test for validation ([#268](https://github.com/VersesTech/gpil/issues/268)) ([7cccead](https://github.com/VersesTech/gpil/commit/7ccceadc341e38c2499be031c5d8782670cc168b))

## [3.1.2](https://github.com/VersesTech/gpil/compare/pyvfg-v3.1.1...pyvfg-v3.1.2) (2025-03-04)


### Bug Fixes

* GPIL-382 vfg_upgrade should convert the version of a 030 vfg to 040 ([#267](https://github.com/VersesTech/gpil/issues/267)) ([d2bb242](https://github.com/VersesTech/gpil/commit/d2bb242208a2d67cb9aa64b301287c7b1dec4c49))
* vfg_upgrade should convert a 030 vfg to 040 ([d2bb242](https://github.com/VersesTech/gpil/commit/d2bb242208a2d67cb9aa64b301287c7b1dec4c49))

## [3.1.1](https://github.com/VersesTech/gpil/compare/pyvfg-v3.1.0...pyvfg-v3.1.1) (2025-03-03)


### Bug Fixes

* GPIL-382 the Factor class failed to generate schema ([#265](https://github.com/VersesTech/gpil/issues/265)) ([effaa53](https://github.com/VersesTech/gpil/commit/effaa5302c37bb8dedbfb15631d4d88b5c0efaeb))

## [3.1.0](https://github.com/VersesTech/gpil/compare/pyvfg-v3.0.3...pyvfg-v3.1.0) (2025-03-01)


### Features

* GPIL-328 extended, model-specific validation with optional correction + VFG performance improvements ([#260](https://github.com/VersesTech/gpil/issues/260)) ([7264603](https://github.com/VersesTech/gpil/commit/7264603e2414b62ba2450fdba7fc7af4bde2a34f))

## [3.0.3](https://github.com/VersesTech/gpil/compare/pyvfg-v3.0.2...pyvfg-v3.0.3) (2025-02-13)


### Bug Fixes

* copied validation tests from gpil-pipeline to ensure validate_graph() functions identically to previously. ([e64fbb7](https://github.com/VersesTech/gpil/commit/e64fbb77cd147529c2643f439127e9c5027ee35e))
* GPIL-0 validation should fail the same items that gpil-pipeline does ([#250](https://github.com/VersesTech/gpil/issues/250)) ([e64fbb7](https://github.com/VersesTech/gpil/commit/e64fbb77cd147529c2643f439127e9c5027ee35e))

## [3.0.2](https://github.com/VersesTech/gpil/compare/pyvfg-v3.0.1...pyvfg-v3.0.2) (2025-02-11)


### Bug Fixes

* GPIL-337 fixes for compatibility with shipped library ([#248](https://github.com/VersesTech/gpil/issues/248)) ([2f95d9c](https://github.com/VersesTech/gpil/commit/2f95d9c72c562ad9d91b7cb5d05aa79bc1520d0c))

## [3.0.1](https://github.com/VersesTech/gpil/compare/pyvfg-v3.0.0...pyvfg-v3.0.1) (2025-02-07)


### Bug Fixes

* GPIL-0 vfg_from_json needs to accept string or dict ([#245](https://github.com/VersesTech/gpil/issues/245)) ([7bed585](https://github.com/VersesTech/gpil/commit/7bed5858c3e78fbd9813c55e5dabdd1dacba2378))

## [3.0.0](https://github.com/VersesTech/gpil/compare/pyvfg-v2.1.3...pyvfg-v3.0.0) (2025-02-07)


### ⚠ BREAKING CHANGES

* GPIL-337 POMDP online learning ([#242](https://github.com/VersesTech/gpil/issues/242))

### Features

* GPIL-337 POMDP online learning ([#242](https://github.com/VersesTech/gpil/issues/242)) ([5728a81](https://github.com/VersesTech/gpil/commit/5728a81c6cc1e46f6f834c3667a5a75b89c18ceb))

## [2.1.3](https://github.com/VersesTech/gpil/compare/pyvfg-v2.1.2...pyvfg-v2.1.3) (2025-02-07)


### Bug Fixes

* GPIL-0 ValidationError should be an Exception ([#243](https://github.com/VersesTech/gpil/issues/243)) ([f3f4f86](https://github.com/VersesTech/gpil/commit/f3f4f86ab066f713d1a343c2a8e2b8b5874fa3de))

## [2.1.2](https://github.com/VersesTech/gpil/compare/pyvfg-v2.1.1...pyvfg-v2.1.2) (2025-02-06)


### Bug Fixes

* trigger new release ([dbd2ab1](https://github.com/VersesTech/gpil/commit/dbd2ab1131ebcb18687a21da990a315487f362f7))
