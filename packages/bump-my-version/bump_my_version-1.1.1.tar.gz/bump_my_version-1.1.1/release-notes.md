[Compare the full difference.](https://github.com/callowayproject/bump-my-version/compare/1.1.0...1.1.1)

### Fixes

- Fix fallback search pattern in files. [51ea69f](https://github.com/callowayproject/bump-my-version/commit/51ea69ffb0c31fd311f386a35e27dc0eee0da3d6)
    
  Refactor `_contains_change_pattern` method by removing unused `context` parameter.

  Replace version config usage with `DEFAULT_CONFIG` to provide correct fallback logic.

  Minor test update to align with changes.
- Fixes lack of rendering in moveable tags. [d201dff](https://github.com/callowayproject/bump-my-version/commit/d201dffb4f96fc58d946451f4799194869316ca4)
    
