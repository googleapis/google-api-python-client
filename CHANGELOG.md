# Changelog

## [2.2.0](https://www.github.com/googleapis/google-api-python-client/compare/v2.1.0...v2.2.0) (2021-04-13)


### Features

* Adds support for errors.py to also use 'errors' for error_details  ([#1281](https://www.github.com/googleapis/google-api-python-client/issues/1281)) ([a5d2081](https://www.github.com/googleapis/google-api-python-client/commit/a5d20813e8d7589b0cec030c149748e53ea555a5))

## [2.1.0](https://www.github.com/googleapis/google-api-python-client/compare/v2.0.2...v2.1.0) (2021-03-31)


### Features

* add status_code property on http error handling ([#1185](https://www.github.com/googleapis/google-api-python-client/issues/1185)) ([db2a766](https://www.github.com/googleapis/google-api-python-client/commit/db2a766bbd976742f6ef10d721d8423c8ac9246d))


### Bug Fixes

* Change default of `static_discovery` when `discoveryServiceUrl` set ([#1261](https://www.github.com/googleapis/google-api-python-client/issues/1261)) ([3b4f2e2](https://www.github.com/googleapis/google-api-python-client/commit/3b4f2e243709132b5ca41a3c23853d5067dfb0ab))
* correct api version in oauth-installed.md ([#1258](https://www.github.com/googleapis/google-api-python-client/issues/1258)) ([d1a255f](https://www.github.com/googleapis/google-api-python-client/commit/d1a255fcbeaa36f615cede720692fea2b9f894db))
* fix .close() ([#1231](https://www.github.com/googleapis/google-api-python-client/issues/1231)) ([a9583f7](https://www.github.com/googleapis/google-api-python-client/commit/a9583f712d13c67aa282d14cd30e00999b530d7c))
* Resolve issue where num_retries would have no effect ([#1244](https://www.github.com/googleapis/google-api-python-client/issues/1244)) ([c518472](https://www.github.com/googleapis/google-api-python-client/commit/c518472e836c32ba2ff5e8480ab5a7643f722d46))


### Documentation

* Distinguish between public/private docs in 2.0 guide ([#1226](https://www.github.com/googleapis/google-api-python-client/issues/1226)) ([a6f1706](https://www.github.com/googleapis/google-api-python-client/commit/a6f17066caf6e911b7e94e8feab52fa3af2def1b))
* Update README to promote cloud client libraries ([#1252](https://www.github.com/googleapis/google-api-python-client/issues/1252)) ([22807c9](https://www.github.com/googleapis/google-api-python-client/commit/22807c92ce754ff3d60f240ec5c38de50c5b654b))

### [2.0.2](https://www.github.com/googleapis/google-api-python-client/compare/v2.0.1...v2.0.2) (2021-03-04)


### Bug Fixes

* Include discovery artifacts in published package ([#1221](https://www.github.com/googleapis/google-api-python-client/issues/1221)) ([ad618d0](https://www.github.com/googleapis/google-api-python-client/commit/ad618d0b266b86a795871d946367552905f4ccb6))

### [2.0.1](https://www.github.com/googleapis/google-api-python-client/compare/v2.0.0...v2.0.1) (2021-03-04)


### Bug Fixes

* add static discovery docs  ([#1216](https://www.github.com/googleapis/google-api-python-client/issues/1216)) ([b5d33d6](https://www.github.com/googleapis/google-api-python-client/commit/b5d33d6d520ca9589eefd08d34fe96844f420bce))


### Documentation

* add a link to the migration guide in the changelog ([#1213](https://www.github.com/googleapis/google-api-python-client/issues/1213)) ([b85da5b](https://www.github.com/googleapis/google-api-python-client/commit/b85da5bb7d6d6da60ff611221d3c4719eadb478a))

## [2.0.0](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.8...v2.0.0) (2021-03-03)


### ⚠ BREAKING CHANGES

The 2.0 release of `google-api-python-client` is a significant upgrade compared to v1. Please see the [Migration Guide](UPGRADING.md) for more information.

* **deps:** require 3.6+.  (#961)

### Features

* Add support for using static discovery documents ([#1109](https://www.github.com/googleapis/google-api-python-client/issues/1109)) ([32d1c59](https://www.github.com/googleapis/google-api-python-client/commit/32d1c597b364e2641eca33ccf6df802bb218eea1))
* Update synth.py to copy discovery files from discovery-artifact-manager ([#1104](https://www.github.com/googleapis/google-api-python-client/issues/1104)) ([af918e8](https://www.github.com/googleapis/google-api-python-client/commit/af918e8ef422438aaca0c468de8b3b2c184d884e))


### Bug Fixes

* Catch ECONNRESET and other errors more reliably ([#1147](https://www.github.com/googleapis/google-api-python-client/issues/1147)) ([ae9cd99](https://www.github.com/googleapis/google-api-python-client/commit/ae9cd99134160a5540e6f8d6d33d855122854e10))
* **deps:** add upper-bound google-auth dependency ([#1180](https://www.github.com/googleapis/google-api-python-client/issues/1180)) ([c687f42](https://www.github.com/googleapis/google-api-python-client/commit/c687f4207b9c574e539a7eab75201a58f2e91f35))
* handle error on service not enabled ([#1117](https://www.github.com/googleapis/google-api-python-client/issues/1117)) ([c691283](https://www.github.com/googleapis/google-api-python-client/commit/c6912836e88eea45aef7d515383e549082d37717))
* Improve support for error_details ([#1126](https://www.github.com/googleapis/google-api-python-client/issues/1126)) ([e6a1da3](https://www.github.com/googleapis/google-api-python-client/commit/e6a1da3542e230e5287863f339ce1d28292cd92f))
* MediaFileUpload error if file does not exist ([#1127](https://www.github.com/googleapis/google-api-python-client/issues/1127)) ([2c6d029](https://www.github.com/googleapis/google-api-python-client/commit/2c6d0297851c806ef850ca23686c51ca5878ac48))
* replace deprecated socket.error with OSError ([#1161](https://www.github.com/googleapis/google-api-python-client/issues/1161)) ([b7b9986](https://www.github.com/googleapis/google-api-python-client/commit/b7b9986fe13c483eeefb77673b4091911978ee46))
* Use logging level info when file_cache is not available ([#1125](https://www.github.com/googleapis/google-api-python-client/issues/1125)) ([0b32e69](https://www.github.com/googleapis/google-api-python-client/commit/0b32e69900eafec2cd1197ba054d4f9a765a3f29))


### Miscellaneous Chores

* **deps:** require 3.6+ ([#961](https://www.github.com/googleapis/google-api-python-client/issues/961)) ([8325d24](https://www.github.com/googleapis/google-api-python-client/commit/8325d24acaa2b2077acaaea26ea5fafb6dd856c5))


### Documentation

* add networkconnectivity v1alpha1 ([#1176](https://www.github.com/googleapis/google-api-python-client/issues/1176)) ([91b61d3](https://www.github.com/googleapis/google-api-python-client/commit/91b61d3272de9b5aebad0cf1eb76ca53c24f22f9))
* Delete redundant oauth-web.md ([#1142](https://www.github.com/googleapis/google-api-python-client/issues/1142)) ([70bc6c9](https://www.github.com/googleapis/google-api-python-client/commit/70bc6c9db99eed5af7536b87448bd9323db9320b))
* fix MediaIoBaseUpload broken link ([#1112](https://www.github.com/googleapis/google-api-python-client/issues/1112)) ([334b6e6](https://www.github.com/googleapis/google-api-python-client/commit/334b6e6d9e4924398e57bad2e53747584abf8cf4))
* fix regression with incorrect args order in docs ([#1141](https://www.github.com/googleapis/google-api-python-client/issues/1141)) ([4249a7b](https://www.github.com/googleapis/google-api-python-client/commit/4249a7b92e891d1ecaf93944ca9c062ffbd54f77))
* fix typo in thread safety example code ([#1100](https://www.github.com/googleapis/google-api-python-client/issues/1100)) ([5ae088d](https://www.github.com/googleapis/google-api-python-client/commit/5ae088dc027b89517b896a89a0aeb2ca80f492cf))
* Reduce noisy changes in docs regen ([#1135](https://www.github.com/googleapis/google-api-python-client/issues/1135)) ([b1b0c83](https://www.github.com/googleapis/google-api-python-client/commit/b1b0c83ae0737e7b63cb77e4e7757213a216b88e))
* update docs/dyn ([#1096](https://www.github.com/googleapis/google-api-python-client/issues/1096)) ([c2228be](https://www.github.com/googleapis/google-api-python-client/commit/c2228be4630e279e02a25b51566a0f93b67aa499))
* update guidance on service accounts ([#1120](https://www.github.com/googleapis/google-api-python-client/issues/1120)) ([b2ea122](https://www.github.com/googleapis/google-api-python-client/commit/b2ea122c40ccac09c9e7b0b29f6b2bcca6db107b))

### [1.12.8](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.7...v1.12.8) (2020-11-18)


### Documentation

* add httplib2 authorization to thread_safety ([#1005](https://www.github.com/googleapis/google-api-python-client/issues/1005)) ([205ae59](https://www.github.com/googleapis/google-api-python-client/commit/205ae5988bd89676823088d6c8a7bd17e3beefcf)), closes [#808](https://www.github.com/googleapis/google-api-python-client/issues/808) [#808](https://www.github.com/googleapis/google-api-python-client/issues/808)

### [1.12.7](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.6...v1.12.7) (2020-11-17)


### Documentation

* Update Webmasters API sample ([#1092](https://www.github.com/googleapis/google-api-python-client/issues/1092)) ([12831f3](https://www.github.com/googleapis/google-api-python-client/commit/12831f3e4716292b55b63dd2b08c3351f09b8a15))

### [1.12.6](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.5...v1.12.6) (2020-11-16)


### Documentation

* Change error parsing to check for 'message' ([#1083](https://www.github.com/googleapis/google-api-python-client/issues/1083)) ([a341c5a](https://www.github.com/googleapis/google-api-python-client/commit/a341c5a5e31ba16da109658127b58cb7e5dbeedd)), closes [#1082](https://www.github.com/googleapis/google-api-python-client/issues/1082)
* Update oauth docs to include snippet to get email address of authenticated user ([#1088](https://www.github.com/googleapis/google-api-python-client/issues/1088)) ([25fba64](https://www.github.com/googleapis/google-api-python-client/commit/25fba648ea647b62f2a6edc54ae927c1ed381b45)), closes [#1071](https://www.github.com/googleapis/google-api-python-client/issues/1071)

### [1.12.5](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.4...v1.12.5) (2020-10-22)


### Bug Fixes

* don't raise when downloading zero byte files ([#1074](https://www.github.com/googleapis/google-api-python-client/issues/1074)) ([86d8788](https://www.github.com/googleapis/google-api-python-client/commit/86d8788ee8a766ca6818620f3fd2899be0e44190))

### [1.12.4](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.3...v1.12.4) (2020-10-20)


### Bug Fixes

* don't set content-range on empty uploads ([#1070](https://www.github.com/googleapis/google-api-python-client/issues/1070)) ([af6035f](https://www.github.com/googleapis/google-api-python-client/commit/af6035f6754a155ee6b04bbbc5c39410c7316d6a))


### Documentation

* fix typo in oauth.md ([#1058](https://www.github.com/googleapis/google-api-python-client/issues/1058)) ([30eff9d](https://www.github.com/googleapis/google-api-python-client/commit/30eff9d8276919b8c4e50df2d3b1982594423692))
* update generated docs ([#1053](https://www.github.com/googleapis/google-api-python-client/issues/1053)) ([3e17f89](https://www.github.com/googleapis/google-api-python-client/commit/3e17f8990db54bec16c48c319072799a14f5a53f)), closes [#1049](https://www.github.com/googleapis/google-api-python-client/issues/1049)

### [1.12.3](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.2...v1.12.3) (2020-09-29)


### Bug Fixes

* **deps:** update setup.py to install httplib2>=0.15.0 ([#1050](https://www.github.com/googleapis/google-api-python-client/issues/1050)) ([c00f70d](https://www.github.com/googleapis/google-api-python-client/commit/c00f70d565a002b92374356be087927b131ce135))

### [1.12.2](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.1...v1.12.2) (2020-09-23)


### Bug Fixes

* add method to close httplib2 connections ([#1038](https://www.github.com/googleapis/google-api-python-client/issues/1038)) ([98888da](https://www.github.com/googleapis/google-api-python-client/commit/98888dadf04e7e00524b6de273d28d02d7abc2c0)), closes [#618](https://www.github.com/googleapis/google-api-python-client/issues/618) 

### [1.12.1](https://www.github.com/googleapis/google-api-python-client/compare/v1.12.0...v1.12.1) (2020-09-14)


### Bug Fixes

* **deps:** require six>=1.13.0 ([#1030](https://www.github.com/googleapis/google-api-python-client/issues/1030)) ([4acecc3](https://www.github.com/googleapis/google-api-python-client/commit/4acecc3c0cd31308f9a256f065b7b1d1c3a4798d))

## [1.12.0](https://www.github.com/googleapis/google-api-python-client/compare/v1.11.0...v1.12.0) (2020-09-12)


### Features

* add quota_project, credentials_file, and scopes support ([#1022](https://www.github.com/googleapis/google-api-python-client/issues/1022)) ([790e702](https://www.github.com/googleapis/google-api-python-client/commit/790e70224c8110bfb1191333ce448c2b0fe54ea6))


### Documentation

* convert `print` statement to function ([#988](https://www.github.com/googleapis/google-api-python-client/issues/988)) ([16448bc](https://www.github.com/googleapis/google-api-python-client/commit/16448bc666e032abd83096faadcda56f86f36f18)), closes [#987](https://www.github.com/googleapis/google-api-python-client/issues/987)
* remove http from batch execute docs ([#1003](https://www.github.com/googleapis/google-api-python-client/issues/1003)) ([5028fe7](https://www.github.com/googleapis/google-api-python-client/commit/5028fe76c8075c6594b1999074f91eed7f7dd329)), closes [#1002](https://www.github.com/googleapis/google-api-python-client/issues/1002)

## [1.11.0](https://www.github.com/googleapis/google-api-python-client/compare/v1.10.1...v1.11.0) (2020-08-27)


### Features

* add support for mtls env variables ([#1008](https://www.github.com/googleapis/google-api-python-client/issues/1008)) ([2fc5ca1](https://www.github.com/googleapis/google-api-python-client/commit/2fc5ca1b6aa880aab2067ab7eb96780a1b28d4c7))

### [1.10.1](https://www.github.com/googleapis/google-api-python-client/compare/v1.10.0...v1.10.1) (2020-08-03)


### Bug Fixes

* discovery uses V2 when version is None ([#975](https://www.github.com/googleapis/google-api-python-client/issues/975)) ([cd4e8f4](https://www.github.com/googleapis/google-api-python-client/commit/cd4e8f429422232dd82ef7e9bc685061d5df94a1)), closes [#971](https://www.github.com/googleapis/google-api-python-client/issues/971)


### Documentation

* fix deprecation warnings due to invalid escape sequences. ([#996](https://www.github.com/googleapis/google-api-python-client/issues/996)) ([0f60eda](https://www.github.com/googleapis/google-api-python-client/commit/0f60eda81ea524dcd1358d87b06da701412bb414)), closes [#995](https://www.github.com/googleapis/google-api-python-client/issues/995)
* fix link to service accounts documentation ([#986](https://www.github.com/googleapis/google-api-python-client/issues/986)) ([edb2516](https://www.github.com/googleapis/google-api-python-client/commit/edb2516eb59770546e7960ca633c7be0ca7b1ad4))
* update generated docs ([#981](https://www.github.com/googleapis/google-api-python-client/issues/981)) ([d059ad8](https://www.github.com/googleapis/google-api-python-client/commit/d059ad881c7ae58c67931c48788d0bd7343ab16c))

## [1.10.0](https://www.github.com/googleapis/google-api-python-client/compare/v1.9.3...v1.10.0) (2020-07-15)


### Features

* allow to use 'six.moves.collections_abc.Mapping' in 'client_options.from_dict()' ([#943](https://www.github.com/googleapis/google-api-python-client/issues/943)) ([21af37b](https://www.github.com/googleapis/google-api-python-client/commit/21af37b11ea2d6a89b3df484e1b2fa1d12849510))
* Build universal wheels ([#948](https://www.github.com/googleapis/google-api-python-client/issues/948)) ([3e28a1e](https://www.github.com/googleapis/google-api-python-client/commit/3e28a1e0d47f829182cd92f37475ab91fa5e4afc))
* discovery supports retries ([#967](https://www.github.com/googleapis/google-api-python-client/issues/967)) ([f3348f9](https://www.github.com/googleapis/google-api-python-client/commit/f3348f98bf91a88a28bf61b12b95e391cc3be1ff)), closes [#848](https://www.github.com/googleapis/google-api-python-client/issues/848)


### Documentation

* consolidating and updating the Contribution Guide ([#964](https://www.github.com/googleapis/google-api-python-client/issues/964)) ([63f97f3](https://www.github.com/googleapis/google-api-python-client/commit/63f97f37daee37a725eb05df3097b20d5d4eaaf0)), closes [#963](https://www.github.com/googleapis/google-api-python-client/issues/963)

### [1.9.3](https://www.github.com/googleapis/google-api-python-client/compare/v1.9.2...v1.9.3) (2020-06-10)


### Bug Fixes

* update GOOGLE_API_USE_MTLS values ([#940](https://www.github.com/googleapis/google-api-python-client/issues/940)) ([19908ed](https://www.github.com/googleapis/google-api-python-client/commit/19908edcd8a3df1db41e34100acc1f15c3c99397))

### [1.9.2](https://www.github.com/googleapis/google-api-python-client/compare/v1.9.1...v1.9.2) (2020-06-04)


### Bug Fixes

* bump api-core version ([#936](https://www.github.com/googleapis/google-api-python-client/issues/936)) ([ee53b3b](https://www.github.com/googleapis/google-api-python-client/commit/ee53b3b32a050874ba4cfb491fb384f94682c824))

### [1.9.1](https://www.github.com/googleapis/google-api-python-client/compare/v1.9.0...v1.9.1) (2020-06-02)


### Bug Fixes

* fix python-api-core dependency issue ([#931](https://www.github.com/googleapis/google-api-python-client/issues/931)) ([42028ed](https://www.github.com/googleapis/google-api-python-client/commit/42028ed2b2be47f85b70eb813185264f1f573d01))

## [1.9.0](https://www.github.com/googleapis/google-api-python-client/compare/v1.8.4...v1.9.0) (2020-06-02)


### Features

* add mtls feature ([#917](https://www.github.com/googleapis/google-api-python-client/issues/917)) ([981eadf](https://www.github.com/googleapis/google-api-python-client/commit/981eadf7cfdb576981d92fcda498c76422821426))
* add templates for python samples projects ([#506](https://www.github.com/googleapis/google-api-python-client/issues/506)) ([#924](https://www.github.com/googleapis/google-api-python-client/issues/924)) ([c482712](https://www.github.com/googleapis/google-api-python-client/commit/c482712935d1c1331e33bd7f9968bd3b2be223bb))

### [1.8.4](https://www.github.com/googleapis/google-api-python-client/compare/v1.8.3...v1.8.4) (2020-05-20)


### Bug Fixes

* don't try to import GAE API in other environments ([#903](https://www.github.com/googleapis/google-api-python-client/issues/903)) ([09e6447](https://www.github.com/googleapis/google-api-python-client/commit/09e644719166aecb21a01b6d5ee9898843e7cd58))
* the turn down date for global batch uri ([#901](https://www.github.com/googleapis/google-api-python-client/issues/901)) ([6ddadd7](https://www.github.com/googleapis/google-api-python-client/commit/6ddadd7753134c671628ad3f4598595b0abb1457))

### [1.8.3](https://www.github.com/googleapis/google-api-python-client/compare/v1.8.2...v1.8.3) (2020-05-01)


### Bug Fixes

* downgrade repetitive logging calls to debug ([#885](https://www.github.com/googleapis/google-api-python-client/issues/885)) ([3bf2781](https://www.github.com/googleapis/google-api-python-client/commit/3bf2781e29cb828409f3a8a21939323286524569)), closes [#781](https://www.github.com/googleapis/google-api-python-client/issues/781)

### [1.8.2](https://www.github.com/googleapis/google-api-python-client/compare/v1.8.1...v1.8.2) (2020-04-21)


### Bug Fixes

* Remove `apiclient.__version__` ([#871](https://www.github.com/googleapis/google-api-python-client/issues/871)) ([c7516a2](https://github.com/googleapis/google-api-python-client/commit/1d8ec6874e1c6081893de7cd7cbc86d1f6580320d)), closes [googleapis#870](https://www.github.com/googleapis/googleapis/issues/870)


### [1.8.1](https://www.github.com/googleapis/google-api-python-client/compare/v1.8.0...v1.8.1) (2020-04-20)


### Bug Fixes

* Adding ConnectionError to retry mechanism ([#822](https://www.github.com/googleapis/google-api-python-client/issues/822)) ([c7516a2](https://www.github.com/googleapis/google-api-python-client/commit/c7516a2ea2c229479633690c109f8763dc0b30ed)), closes [googleapis#558](https://www.github.com/googleapis/googleapis/issues/558)
* replace '-' in method names with '_' ([#863](https://www.github.com/googleapis/google-api-python-client/issues/863)) ([8ed729f](https://www.github.com/googleapis/google-api-python-client/commit/8ed729f1d868a8713ab442bf0bf59e77ba36afb6))

### v1.8.0
  Version 1.8.0

  Release to support API endpoint override.

  New Features
  - Add api endpoint override. ([#829](https://github.com/googleapis/google-api-python-client/pull/829))

  Implementation Changes
  - Don't set http.redirect_codes if the attr doesn't exist and allow more httplib2 versions. ([#841](https://github.com/googleapis/google-api-python-client/pull/841))

### v1.7.12
  Version 1.7.12
  
  Bugfix release
  
  Implementation Changes
  - Look for field 'detail' in error message. ([#739](https://github.com/googleapis/google-api-python-client/pull/739))
  - Exclude 308s from httplib2 redirect codes list ([#813](https://github.com/googleapis/google-api-python-client/pull/813))
  
  Documentation 
  - Remove oauth2client from docs ([#738](https://github.com/googleapis/google-api-python-client/pull/738))
  - Fix typo. ([#745](https://github.com/googleapis/google-api-python-client/pull/745))
  - Remove compatibility badges. ([#746](https://github.com/googleapis/google-api-python-client/pull/746))
  - Fix TypeError: search_analytics_api_sample.py #732 ([#742](https://github.com/googleapis/google-api-python-client/pull/742))
  - Correct response access ([#750](https://github.com/googleapis/google-api-python-client/pull/750))
  - Fix link to API explorer ([#760](https://github.com/googleapis/google-api-python-client/pull/760))
  - Fix argument typo in oauth2 code example ([#763](https://github.com/googleapis/google-api-python-client/pull/763))
  - Recommend install with virtualenv ([#768](https://github.com/googleapis/google-api-python-client/pull/768))
  - Fix capitalization in docs/README.md ([#770](https://github.com/googleapis/google-api-python-client/pull/770))

  - Remove compatibility badges ([#796](https://github.com/googleapis/google-api-python-client/pull/796))
  - Remove mentions of pycrypto ([#799](https://github.com/googleapis/google-api-python-client/pull/799))
  - Fix typo in model.py
  - Add note about Google Ads llibrary ([#814](https://github.com/googleapis/google-api-python-client/pull/814))

  
  Internal / Testing Changes
  - Blacken ([#772](https://github.com/googleapis/google-api-python-client/pull/722))
  - Move kokoro configs ([#832](https://github.com/googleapis/google-api-python-client/pull/832))
  
### v1.7.11
  Version 1.7.11

  Bugfix release

  Implementation Changes
  - Pass library and Python version in x-goog-api-client header ([#734](https://github.com/googleapis/google-api-python-client/pull/734))

  Documentation
  - Fix typo in filename used in 'docs/auth.md' ([#736](https://github.com/googleapis/google-api-python-client/pull/736))

  
### v1.7.10
  Version 1.7.10

  Bugfix release

  Implementation Changes
  - Decode service to utf-8 ([#723](https://github.com/googleapis/google-api-python-client/pull/723))
  - Use print() function in both Python2 and Python 3 ([#722](https://github.com/googleapis/google-api-python-client/pull/722))
  - Make http.MediaFileUpload close its file descriptor ([#600](https://github.com/googleapis/google-api-python-client/pull/600))
  - Never make 'body' required ([#718](https://github.com/googleapis/google-api-python-client/pull/718))

  Documentation
  - Add compatability check badges to README ([#691](https://github.com/googleapis/google-api-python-client/pull/691))
  - Regenerate docs ([#696](https://github.com/googleapis/google-api-python-client/pull/696), [#700](https://github.com/googleapis/google-api-python-client/pull/700))
  - Create index file for dynamically generated docs ([#702](https://github.com/googleapis/google-api-python-client/pull/702))
  - Add docs folder with guides from developers.google.com ([#706](https://github.com/googleapis/google-api-python-client/pull/706), [#710](https://github.com/googleapis/google-api-python-client/pull/710))

  Internal / Testing Changes
  - Fix http.py, lint errors, unit test ([#724](https://github.com/googleapis/google-api-python-client/pull/724))
  - tox.ini: Look for Python syntax errors and undefined names ([#721](https://github.com/googleapis/google-api-python-client/pull/721))


### v1.7.9
  Version 1.7.9

  Bugfix release
  - Remove Django Samples. ([#657](https://github.com/googleapis/google-api-python-client/pull/657))
  - Call request_orig with kwargs ([#658](https://github.com/googleapis/google-api-python-client/pull/658))

### v1.7.8
  Version 1.7.8

  Bugfix release
  - Convert '$' in method name to '_' ([#616](https://github.com/googleapis/google-api-python-client/pull/616))
  - Alias unitest2 import as unittest in test__auth.py ([#613](https://github.com/googleapis/google-api-python-client/pull/613))

### v1.7.7
  Version 1.7.7

    Bugfix release
    - Change xrange to range ([#601](https://github.com/googleapis/google-api-python-client/pull/601))
    - Typo in http.py exception message. ([#602](https://github.com/googleapis/google-api-python-client/pull/602))

    - Announce deprecation of Python 2.7 ([#603](https://github.com/googleapis/google-api-python-client/pull/603))
    - Updates documentation for stopping channel subscriptions ([#598](https://github.com/googleapis/google-api-python-client/pull/598))
    - Adding example for searchAppearance ([#414](https://github.com/googleapis/google-api-python-client/pull/414))

    - Add badges ([#455](https://github.com/googleapis/google-api-python-client/pull/455))

### v1.7.6
  Version 1.7.6

  Bugfix release

  - Add client-side limit for batch requests (#585)

### v1.7.5
  Version 1.7.5

  Bugfix release

  - Fix the client to respect the passed in developerKey and credentials

### v1.7.4
  Version 1.7.4

  Bugfix release

  - Catch ServerNotFoundError to retry the request (#532)

### v1.7.3
  Version 1.7.3

  Bugfix release

  - Make apiclient.sample_tools gracefully fail to import (#525).


### v1.7.2
  Version 1.7.2

  Bugfix release

  - Remove unnecessary check in apiclient/__ini__.py (#522).

### v1.7.1
  Version 1.7.1

  Bugfix release

  - Remove unnecessary check in setup.py (#518).

### v1.7.0
  Version 1.7.0

  This release drops the hard requirement on oauth2client and installs
  google-auth by default instead. oauth2client is still supported but will
  need to be explicitly installed.

  - Drop oauth2client dependency (#499)
  - Include tests in source distribution (#514)

### v1.6.7
  Version 1.6.7

  Bugfix release

  **Note**: The next release of this library will no longer directly depend on
    oauth2client. If you need to use oauth2client, you'll need to explicitly
    install it.

  - Make body optional for requests with no parameters. (#446)
  - Fix retying on socket.timeout. (#495)
  - Match travis matrix with tox testenv. (#498)
  - Remove oauth2client._helpers dependency. (#493)
  - Remove unused keyring test dependency. (#496)
  - discovery.py: remove unused oauth2client import. (#492)
  - Update README to reference GCP API client libraries. (#490)

### v1.6.6
  Version 1.6.6

  Bugfix release

  - Warn when constructing BatchHttpRequest using the legacy batch URI (#488)
  - Increase the default media chunksize to 100MB. (#482)
  - Remove unnecessary parsing of mime headers in HttpRequest.__init__ (#467)

### v1.6.5
  Version 1.6.5

  Bugfix release

  - Proactively refresh credentials when applying and treat a missing
    `access_token` as invalid. Note: This change reveals surprising behavior
    between default credentials and batches. If you allow
    `googleapiclient.discovery.build` to use default credentials *and* specify
    different credentials by providing `batch.execut()` with an explicit `http`
    argument, your individual requests will use the default credentials and
    *not* the credentials specified to the batch http. To avoid this, tell
    `build` explicitly not to use default credentials by specifying
    `build(..., http=httplib2.Http()`. (#469)
  - Remove mutual exclusivity check for developerKey and credentials (#465)
  - Handle unknown media length. (#406)
  - Handle variant error format gracefully. (#459)
  - Avoid testing against Django >= 2.0.0 on Python 2. (#460)

### v1.6.4
  Version 1.6.4

  Bugfix release

  - Warn when google-auth credentials are used but google-auth-httplib2 isn't available. (#443)

### v1.6.3
  Version 1.6.3

  Bugfix release

  - Add notification of maintenance mode to README. (#410)
  - Fix generation of methods with abnormal page token conventions. (#338)
  - Raise ValueError is credentials and developerKey are both specified. (#358)
  - Re-generate documentation. (#364, #373, #401)
  - Fix method signature documentation for multiline required parameters. (#374)
  - Fix ZeroDivisionError in MediaDownloadProgress.progress. (#377)
  - Fix dead link to WebTest in README. (#378)
  - Fix details missing in googleapiclient.errors.HttpError. (#412)
  - Don't treat httplib2.Credentials as oauth credentials. (#425)
  - Various fixes to the Django sample. (#413)

### v1.6.2
  Version 1.6.2

  Bugfix release

  - Fixed a bug where application default credentials would still be used even
    when a developerKey was specified. (#347)
  - Official support for Python 3.5 and 3.6. (#341)
 
### v1.6.1
  Version 1.6.1

  Bugfix release

  - Fixed a bug where using google-auth with scoped credentials would fail. (#328)

### v1.6.0
  Version 1.6.0

  Release to drop support for Python 2.6 and add support for google-auth.

  - Support for Python 2.6 has been dropped. (#319)
  - The credentials argument to discovery.build and discovery.build_from_document
    can be either oauth2client credentials or google-auth credentials. (#319)
  - discovery.build and discovery.build_from_document now unambiguously use the
    http argument to make all requests, including the request for the discovery
    document. (#319)
  - The http and credentials arguments to discovery.build and
    discovery.build_from_document are now mutually exclusive, eliminating a
    buggy edge case. (#319)
  - If neither http or credentials is specified to discovery.build and
    discovery.build_from_document, then Application Default Credentials will
    be used. The library prefers google-auth for this if it is available, but
    can also use oauth2client's implementation. (#319)
  - Fixed resumable upload failure when receiving a 308 response. (#312)
  - Clarified the support versions of Python 3. (#316)

### v1.5.5
  Version 1.5.5

  Bugfix release

  - Allow explicit MIME type specification with media_mime_type keyword argument.
  - Fix unprintable representation of BatchError with default constructor. (#165)
  - Refresh all discovery docs, not just the preferred ones. (#298)
  - Update minimum httplib2 dependency to >=0.9.2.

### v1.5.4
  Version 1.5.4

  Bugfix release

  - Properly handle errors when the API returns a mapping or sequence. (#289)
  - Upgrade to unified uritemplate 3.0.0. (#293)
  - Allow oauth2client 4.0.0, with the caveat that file-based discovery
    caching is disabled.

### v1.5.3
  Version 1.5.3

  Bugfix release

  - Fixed import error with oauth2client >= 3.0.0. (#270)

### v1.5.2
  Version 1.5.2

  Bugfix release

  - Allow using oauth2client >= 1.5.0, < 4.0.0. (#265)
  - Fix project_id argument description. (#257)
  - Retry chunk uploaded on rate limit exceeded errors. (#255)
  - Obtain access token if necessary in BatchHttpRequest.execute(). (#232)
  - Warn when running tests using HttpMock without having a cache. (#261)

### v1.5.1
  Version 1.5.1

  Bugfix release

  - Allow using versions of oauth2client < 2.0.0. (#197)
  - Check both current and new API discovery URL. (#202)
  - Retry http requests on connection errors and timeouts. (#218)
  - Retry http requests on rate limit responses. (#201)
  - Import guards for ssl (for Google App Engine). (#220)
  - Use named loggers instead of the root logger. (#206)
  - New search console example. (#212)

### v1.5.0
  Version 1.5.0

  Release to support oauth2client >= 2.0.0.

  - Fix file stream recognition in Python 3 (#141)
  - Fix non-resumable binary uploads in Python 3 (#147)
  - Default to 'octet-stream' if mimetype detection fails (#157)
  - Handle SSL errors with retries (#160)
  - Fix incompatibility with oauth2client v2.0.0 (#182)

### v1.4.2
  Version 1.4.2

  Add automatic caching for the discovery docs.

### v1.4.1
  Version 1.4.1

  Add the googleapiclient.discovery.Resource.new_batch_http_request method.

### v1.4.0
  Version 1.4.0

  Python 3 support.

### v1.3.2
  Version 1.3.2

  Small bugfix release.

  - Fix an infinite loop for downloading small files.
  - Fix a unicode error in error encoding.
  - Better handling of `content-length` in media requests.
  - Add support for methodPath entries containing colon.

### v1.3.1
  Version 1.3.1

  Quick release for a fix around aliasing in v1.3.

### v1.3
  Version 1.3

  Add support for the Google Application Default Credentials.
  Require python 2.6 as a minimum version.
  Update several API samples.
  Finish splitting out oauth2client repo and update tests.
  Various doc cleanup and bugfixes.

  Two important notes:
    * We've added `googleapiclient` as the primary suggested import
      name, and kept `apiclient` as an alias, in order to have a more
      appropriate import name. At some point, we will remove `apiclient`
      as an alias.
    * Due to an issue around in-place upgrades for Python packages,
      it's not possible to do an upgrade from version 1.2 to 1.3. Instead,
      setup.py attempts to detect this and prevents it. Simply remove
      the previous version and reinstall to fix this.

### v1.2
  Version 1.2

  The use of the gflags library is now deprecated, and is no longer a
    dependency. If you are still using the oauth2client.tools.run() function
    then include gflags as a dependency of your application or switch to
    oauth2client.tools.run_flow.
  Samples have been updated to use the new apiclient.sample_tools, and no
    longer use gflags.
  Added support for the experimental Object Change Notification, as found in
    the Cloud Storage API.
  The oauth2client App Engine decorators are now threadsafe.

  - Use the following redirects feature of httplib2 where it returns the
    ultimate URL after a series of redirects to avoid multiple hops for every
    resumable media upload request.
  - Updated AdSense Management API samples to V1.3
  - Add option to automatically retry requests.
  - Ability to list registered keys in multistore_file.
  - User-agent must contain (gzip).
  - The 'method' parameter for httplib2 is not positional. This would cause
    spurious warnings in the logging.
  - Making OAuth2Decorator more extensible. Fixes Issue 256.
  - Update AdExchange Buyer API examples to version v1.2.


### v1.1
  Version 1.1

  Add PEM support to SignedJWTAssertionCredentials (used to only support
  PKCS12 formatted keys). Note that if you use PEM formatted keys you can use
  PyCrypto 2.6 or later instead of OpenSSL.

  Allow deserialized discovery docs to be passed to build_from_document().

  - Make ResumableUploadError derive from HttpError.
  - Many changes to move all the closures in apiclient.discovery into real
  -  classes and objects.
  - Make from_json behavior inheritable.
  - Expose the full token response in OAuth2Client and OAuth2Decorator.
  - Handle reasons that are None.
  - Added support for NDB based storing of oauth2client objects.
  - Update grant_type for AssertionCredentials.
  - Adding a .revoke() to Credentials. Closes issue 98.
  - Modify oauth2client.multistore_file to store and retrieve credentials
    using an arbitrary key.
  - Don't accept 403 challenges by default for auth challenges.
  - Set httplib2.RETRIES to 1.
  - Consolidate handling of scopes.
  - Upgrade to httplib2 version 0.8.
  - Allow setting the response_type in OAuth2WebServerFlow.
  - Ensure that dataWrapper feature is checked before using the 'data' value.
  - HMAC verification does not use a constant time algorithm.

### v1.0
 Version 1.0

  - Changes to the code for running tests and building releases.

### v1.0c3
 Version 1.0 Release Candidate 3

  - In samples and oauth2 decorator, escape untrusted content before displaying it.
  - Do not allow credentials files to be symlinks.
  - Add XSRF protection to oauth2decorator callback 'state'.
  - Handle uploading chunked media by stream.
  - Handle passing streams directly to httplib2.
  - Add support for Google Compute Engine service accounts.
  - Flows no longer need to be saved between uses.
  - Change GET to POST if URI is too long. Fixes issue #96.
  - Add a keyring based Storage.
  - More robust picking up JSON error responses.
  - Make batch errors align with normal errors.
  - Add a Google Compute sample.
  - Token refresh to work with 'old' GData API
  - Loading of client_secrets JSON file backed by a cache.
  - Switch to new discovery path parameters.
  - Add support for additionalProperties when printing schema'd objects.
  - Fix media upload parameter names. Reviewed in http://codereview.appspot.com/6374062/
  - oauth2client support for URL-encoded format of exchange token response (e.g.  Facebook)
  - Build cleaner and easier to read docs for dynamic surfaces.

### v1.0c2
 Version 1.0 Release Candidate 2

  - Parameter values of None should be treated as missing. Fixes issue #144.
  - Distribute the samples separately from the library source. Fixes issue #155.
  - Move all remaining samples over to client_secrets.json. Fixes issue #156.
  - Make locked_file.py understand win32file primitives for better awesomeness.

### v1.0c1
 Version 1.0 Release Candidate 1

 - Documentation for the library has switched to epydoc:
     http://google-api-python-client.googlecode.com/hg/docs/epy/index.html
 - Many improvements for media support:
   * Added media download support, including resumable downloads.
   * Better handling of streams that report their size as 0.
   * Update Media Upload to include io.Base and also fix some bugs.
 - OAuth bug fixes and improvements.
   * Remove OAuth 1.0 support.
   * Added credentials_from_code and credentials_from_clientsecrets_and_code.
   * Make oauth2client support Windows-friendly locking.
   * Fix bug in StorageByKeyName.
   * Fix None handling in Django fields. Reviewed in http://codereview.appspot.com/6298084/. Fixes issue #128.
 - Add epydoc generated docs. Reviewed in http://codereview.appspot.com/6305043/
 - Move to PEP386 compliant version numbers.
 - New and updated samples
   * Ad Exchange Buyer API v1 code samples.
   * Automatically generate Samples wiki page from README files.
   * Update Google Prediction samples.
   * Add a Tasks sample that demonstrates Service accounts.
   * new analytics api samples. Reviewed here: http://codereview.appspot.com/5494058/
 - Convert all inline samples to the Farm API for consistency.

### v1.0beta8
 - Updated meda upload support.
 - Many fixes for batch requests.
 - Better handling for requests that don't require a body.
 - Fix issues with Google App Engine Python 2.7 runtime.
 - Better support for proxies.
 - All Storages now have a .delete() method.
 - Important changes which might break your code:
    * apiclient.anyjson has moved to oauth2client.anyjson.
    * Some calls, for example, taskqueue().lease() used to require a parameter
      named body. In this new release only methods that really need to send a body
      require a body parameter, and so you may get errors about an unknown
      'body' parameter in your call. The solution is to remove the unneeded
      body={} parameter.

### v1.0beta7
 - Support for batch requests.  http://code.google.com/p/google-api-python-client/wiki/Batch
 - Support for media upload.  http://code.google.com/p/google-api-python-client/wiki/MediaUpload
 - Better handling for APIs that return something other than JSON.
 - Major cleanup and consolidation of the samples.
 - Bug fixes and other enhancements:
   72  Defect  Appengine OAuth2Decorator: Convert redirect address to string
   22  Defect  Better error handling for unknown service name or version
   48  Defect  StorageByKeyName().get() has side effects
   50  Defect  Need sample client code for Admin Audit API
   28  Defect  better comments for app engine sample   Nov 9
   63  Enhancement Let OAuth2Decorator take a list of scope
