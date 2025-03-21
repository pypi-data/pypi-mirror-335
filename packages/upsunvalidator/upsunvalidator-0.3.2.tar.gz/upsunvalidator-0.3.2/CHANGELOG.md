# Changelog

## [0.3.2] - 2025-03-20

- Renames `templates` as `examples in comments and method names. Previous methods exist as wrappers only, but will be deprecated in a future release.
- Restructures tests to leave only `examples` within the package, not the tests or invalid cases.
- Reinstates CLI as a local testing tool, as this makes updating validation when working with MCP a smoother process instead of rewriting/committing a `test.py` file. This adds but does not change previous behavior. Also adds an `examples` command to list, and an `--example` option flag to validate built-in examples
- Updates missing items in the CHANGELOG

## [0.3.1] - 2025-03-13

Multiple small changes made ahead of internal demo:

- Adding valid tests for hugo, django-pgvector, and django-redis-celery
- Fixed up sorting hugos between valid and invalid

## [0.3.0] - 2025-03-13

Release tools: changed from `flit` to `setuptools_scm`.

## [0.2.5] - 2025-03-13

Automatic versioning for releases was implemented.

## [0.2.4] - 2025-03-13

All tests were moved within the package itself.

## [0.2.3] - 2025-03-13

New tag to bundle previous incremental changes.

## [0.2.2] - 2025-03-13

Packaging automation was updated.

## [0.2.1] - 2025-03-13

Valid tests were moved within the package itself.

## [0.2.0] - 2025-03-12

Library was restructured to prioritize string-based validation prompts for the MCP use case.

## [0.1.2] - 2025-03-12

### Additional post-release fixes

Running PR for additional tweaks and fixes following the initial release:

- Single installation path for now
- [Update upgrade instructions](https://github.com/Jeck-ai/upsunvalidator/issues/13)
- [Removes `generate`/`gen` command placeholder, as ultimately out of scope](https://github.com/Jeck-ai/upsunvalidator/issues/16)
- [Raises `ValidationError` when top-level keys are included, instead of silently failing](https://github.com/Jeck-ai/upsunvalidator/issues/17), and handle top-level duplicates within the same file.

## [0.1.1] - 2025-03-11

### Initial release follow-up

Small updates to issue templates and installation instructions post initial release.

## [0.1.0] - 2025-03-11

### Initial release

`0.1.0` is the initial release of `upsunvalidator`, an open-source project written in Python that adds additional validation capabilities to upstream Platform.sh and Upsun schemas.
It allows you to validate configuration for those PaaS providers locally prior to push, covering cases not yet addressed by those upstream schemas that might otherwise create friction during onboarding and testing. 

In this first release, `upsunvalidator` contains the following capabilities:

1. Leverages the pre-existing schema validation for Platform.sh and Upsun provided by the `app:config-validate` command.
1. Validates valid service versions for both applications and services, as documented in the Platform.sh and Upsun public documentation.
1. Validates valid PHP extensions for PHP application types, as documented in the Platform.sh and Upsun public documentation.
1. When service types, versions, and extensions are invalid, this tool will make a guess of the users intent, providing recommended changes.
1. Leverages a collection of working Platform.sh and Upsun templates as a part of internal testing.
1. Understands multi-app configurations (combined configuration within a single `.upsun/config.yaml` file, `.platform/applications.yaml` file, or multiple `.platform.app.yaml` files throughout the repo.)
1. Understands configuration combination for Upsun (all files within `.upsun` are merged into a single configuration describing the environment).

At this point, this library does not yet handle:

1. Nix-based composable images (the `stack` key).
1. Testing valid (or invalid) examples against actual deployments to verify validation additions.
1. Configuration generation (`generate` command).
1. `source.root` and path execution within hooks. That is, validating that a called script is located at the expected dest and executable.
1. Regular, scheduled updates of upstream schemas, registries, and extensions list.
1. Undefined service-to-relationship matches.
1. Undefined route-to-application matches.
