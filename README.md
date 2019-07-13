# jupyterlab-dash

[![Binder](https://beta.mybinder.org/badge.svg)](https://mybinder.org/v2/gh/plotly/jupyterlab-dash/master?urlpath=lab%2Ftree%2Fnotebooks)

A JupyterLab extension for rendering Plotly Dash apps as a separate window in JupyterLab :tada:

![JupyterLab and Dash Demo Video](https://user-images.githubusercontent.com/1280389/47668836-da9f4280-db7f-11e8-8523-8663b6a5347f.gif)

**Note:**: This extension does not currently support Windows or Python 2

## Prerequisites

- JupyterLab 1.0.0
- Dash

## Installation

The jupyterlab-dash library requires both a Python package and a JupyterLab
extension.

First, install the Python package using either pip...

```
$ pip install "jupyterlab>=1.0" jupyterlab-dash==0.1.0a3
```

or conda (but not both!).

```
$ conda install -c plotly -c defaults -c conda-forge "jupyterlab>=1.0" jupyterlab-dash=0.1.0a3
```

Then, install the JupyterLab extension. v6.17.1 of node works, and node 8.x.x or 10+ should also work. 
```
$ jupyter labextension install jupyterlab-dash@0.1.0-alpha.3
```

## Development Installation

If you'd like to install jupyterlab-dash for development

```bash
$ git clone https://github.com/plotly/jupyterlab-dash
$ cd jupyterlab-dash

# Install Python package
$ pip install -e .

# Install Javascript dependencies
$ npm install # or yarn

# Build JupyterLab extension
$ npm run build # or yarn build
$ jupyter labextension link .
```

To rebuild the JupyterLab extension:

```bash
$ npm run build
$ jupyter lab build
```

To rebuild the JupyterLab extension automatically as the source changes:

```bash
# In one terminal tab, watch the jupyterlab-dash directory
$ npm run watch # or yarn watch

# In another terminal tab, run jupyterlab with the watch flag
$ jupyter lab --watch
```

## Usage

```python
import jupyterlab_dash
import dash
import dash_html_components as html

viewer = jupyterlab_dash.AppViewer()

app = dash.Dash(__name__)

app.layout = html.Div('Hello World')

viewer.show(app)
```
