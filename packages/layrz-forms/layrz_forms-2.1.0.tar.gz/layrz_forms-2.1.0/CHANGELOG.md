# Changelog

## 2.1.0

- Migrated to use `ruff` and `mypy` for linting and type checking
- Improvements on documentation to use PEP style

## 2.0.1

- Removed namespace scan in `pyproject.toml` to avoid issues with other libraries

## 2.0.0

- Due to a incompatibility with shared namespaces, we changed the usage of the library from `from layrz import forms` to `import layrz_forms as forms`

## 1.0.12

- Fixed issue with nested fields (Previous fix was not working properly)

## 1.0.11

- Fixed issue with nested fields

## 1.0.10

- Fixed issue with nested forms, now will be validated correctly

## v1.0.9

- Migrated to GitHub

## v1.0.7

- Fixes on package namespace

## v1.0.6

- Update logic for required in Number and Id fields

## v1.0.5

- Added support for nested fields along with forms
- Added extra condition at the moment of validate the type of the field (boolean, number, id) to avoid false invalid when is not required

## v1.0.4

- Hotfix

## v1.0.3

- Removed multiprocessing option

## v1.0.2

- hotfix

## v1.0.1

- Fixed long_description in setup

## v1.0.0

- Initial release
