from setuptools import setup

setup(
    name='jupyterlab-dash',
    version='0.1',
    packages=['jupyterlab_dash'],
    install_requires=['dash', 'jupyter-server-proxy']
)
