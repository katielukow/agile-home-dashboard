# Release Workflow

This document outlines the release workflow for release.

## Creating a New Release

To create a new release, follow these steps:

1. **Prepare the Release:**
   -  Create a new branch for the release (i.e. `v0.X.0`) from `develop`.
   -  Increment the following:
         -  The version number in the `pyproject.toml` file.
         -  The `CHANGELOG.md` version with the changes for the new version.
    -  Open a PR to the `main` branch. Once the PR is merged, proceed to the next step.


2. **Create a GitHub Release:**
   -  Go to the "Releases" section on GitHub.
   -  Click "Draft a new release".
   -  Select the `main` branch as the release target.
   -  Create a release tag (`v0.X.0`):
      - Note: GitHub provides the option to create this tag on publish if you start typing a new tag
   -  Fill in the release title and description. Add any major changes and link to the `CHANGELOG.md` for a list of total changes.
   -  Click "Publish release" to create the release.

3. **Merge Main into Develop**
   -  Finally, open a PR from `main` to `develop` to synchronise the release changes. This ensures `develop` is always ahead of `main`, reducing the work required for future releases.
