# jupyterlab_dash

A JupyterLab extension for rendering Plotly Dash apps as a separate window in JupyterLab :tada:

![JupyterLab and Dash Demo Video](https://user-images.githubusercontent.com/1280389/47668836-da9f4280-db7f-11e8-8523-8663b6a5347f.gif)

**Note:**: This extension does not currently support Windows or Python 2

## Prerequisites

* JupyterLab


## Installation

We haven't published the component yet, but we will soon. In the meantime, you'll need to clone the repo and install manually:

```bash
git clone https://github.com/plotly/jupyterlab-dash
cd jupyterlab-dash
# Install Python package
pip install -e .
# Install Javascript dependencies
npm install # or yarn
# Build JupyterLab extension
npm run build # or yarn build
jupyter labextension link .
```

To rebuild the JupyterLab extension:

```bash
npm run build
jupyter lab build
```

To rebuild the JupyterLab extension automatically as the source changes:

```bash
# In one terminal tab, watch the jupyterlab-dash directory
npm run watch # or yarn watch
# In another terminal tab, run jupyterlab with the watch flag
jupyter lab --watch
```

## Usage

```python
import jupyterlab_dash
import dash
import dash_html_components as html

viewer = jupyterlab_dash.AppViewer(port=8050)

app = dash.Dash(__name__)

app.layout = html.Div('Hello World')

viewer.show(app)
```
