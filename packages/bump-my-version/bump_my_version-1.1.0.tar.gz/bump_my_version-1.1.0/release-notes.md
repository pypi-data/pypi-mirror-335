[Compare the full difference.](https://github.com/callowayproject/bump-my-version/compare/1.0.2...1.1.0)

### Fixes

- Refactor Mercurial SCM support and improve test coverage. [acd94d1](https://github.com/callowayproject/bump-my-version/commit/acd94d150b0bca2fbec354a50ae9b36bdb3cff75)
    
  Revamped the Mercurial SCM implementation with new features including full tag retrieval, commit handling, and clean working directory assertion. Enhanced test suite with new Mercurial-specific tests for functionality and edge cases.
- Fixed the test_bump_nested_regex function to use utc time. [7d33dff](https://github.com/callowayproject/bump-my-version/commit/7d33dffaf38e7816202ddff3e9a9cc6a66b57fcb)
    
  Code in the test function used the machine local time instead of UTC
  time. This made the test fail if the user was not in UTC time, as the
  fixture tested against a bumped time using `utcnow`

  Added a recipe to justfile to run the tests and open the coverage report
  in a default web browser
- Fix caching in action. [d3b9f76](https://github.com/callowayproject/bump-my-version/commit/d3b9f76d2422b6b2da16c3a4d08b2c572758740a)
    
### New

- Added to the setup section in the contribution doc for the devenv.nix shell. [f94cc27](https://github.com/callowayproject/bump-my-version/commit/f94cc274bdac4d13969254445ff414311407ebcd)
    
- Added devenv.nix and justfile. [653d917](https://github.com/callowayproject/bump-my-version/commit/653d917885b7e04c18a59b7b04c0d34a7ff186d8)
    
  Addition of devenv.nix allows developers to easily create hermetic
  environments in order to develop this package. This greatly simplifies
  the setup of the environment, and utilizes uv's tooling to create the
  virtual environment(s). Devenv.nix can also handle git-hooks, but that
  is already handled via the .pre-commit-config.yaml file.

  The justfile includes some helpful starter recipes. Additional recipes
  can be added, such as build and publishing of the package/Docker.
### Other

- [pre-commit.ci] pre-commit autoupdate. [a85b47f](https://github.com/callowayproject/bump-my-version/commit/a85b47fd333c8e115085c44bf6b003d3010ef9f3)
    
  **updates:** - [github.com/astral-sh/ruff-pre-commit: v0.9.9 → v0.11.0](https://github.com/astral-sh/ruff-pre-commit/compare/v0.9.9...v0.11.0)

### Updates

- Improved mercurial test coverage. [e35eee1](https://github.com/callowayproject/bump-my-version/commit/e35eee17098731c8465c58ec33d29be5f9c13dea)
    
