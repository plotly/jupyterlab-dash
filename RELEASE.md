## Check out the most recent version of master
```
$ git checkout master
$ git stash
$ git pull
```

## Update CHANGELOG and README
Update the `CHANGELOG.md` file with changes since the last release.

Update the README with the new version numbers, and push README updates.

Commit and push these updates.

## Release jupyterlab-dash to PyPI
Install `twine`

```
$ pip install twine
```

Update version in `jupyterlab_dash/__version__.py`.
This will be referred to as version `A.B.C` below.

Build and upload
```
$ python setup.py upload
```

## Release jupyterlab-dash to NPM
First [install yarn](https://yarnpkg.com/lang/en/docs/install/).

To publish a pre-release
```
yarn publish --access public --tag next
```

To publish a final release
```
yarn publish --access public
```

Enter the new version number in the prompt

Then tag the release (Where `X.Y.Z` is the version entered above)

```
$ git tag jupyterlab-vX.Y.Z
$ git push origin jupyterlab-vX.Y.Z
```

## Add GitHub Release entry

Go to https://github.com/plotly/jupyterlab-dash/releases and "Draft a new release"

Enter the `vA.B.C` tag

Make "Release title" the same string as the tag.

Copy changelog section for this version as the "Describe this release"
