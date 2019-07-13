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

## Release jupyterlab-dash to anaconda cloud

From a conda environment, install `anaconda-client`.

Run `anaconda login` from the terminal and enter the plotly channel credentials.

Build the conda package

```
$ conda build recipe/
```

Upload conda package by running the `anaconda upload ...` command displayed at
then end of the conda build command above.

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

## Add GitHub Release entry

Go to https://github.com/plotly/jupyterlab-dash/releases and "Draft a new release"

Enter the `vA.B.C` tag

Make "Release title" the same string as the tag.

Copy changelog section for this version as the "Describe this release"
