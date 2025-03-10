# Packaging (`bumpversion`, `twine`)

## Initialization

* The release system is entirely managed by GitLab. Whenever you publish a
  new release, GitLab builds a new wheel and make it available through
  the repository.
* Install `bumpversion`:

```bash
apt install bumpversion
```

## New release

* Update the changelog `HISTORY.md`, then add and commit this change:

```bash
git add README.md
git commit -m "Updated README.md"
```

* Increase the version number using `poetry-bumpversion`:

```bash
bumpversion patch  # Possible values: major / minor / patch
git push
git push --tags
```

* Create a release through the GitHub interface.
