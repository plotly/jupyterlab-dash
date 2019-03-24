import multiprocessing
import socket
import uuid
import time
from threading import Timer
import platform

from queue import Empty
from urllib.parse import urlparse
import sys
import IPython
from ipykernel.comm import Comm


class StdErrorQueue(object):
    def __init__(self):
        self.queue = multiprocessing.Queue()

    def write(self, v):
        self.queue.put(v)

    def flush(self):
        sys.__stderr__.flush()


class AppViewer(object):
    _dash_comm = Comm(target_name='dash_viewer')
    _jupyterlab_url = None

    def __init__(self, host='localhost', port=None):

        if platform.system() == 'Windows':
            raise OSError("""\
Unfortunately, the jupyterlab-dash extension is not yet
compatible with Windows""")

        self.server_process = None
        self.uid = str(uuid.uuid4())
        self.host = host
        self.stderr_queue = StdErrorQueue()

        if port:
            self.port = port
        else:
            # Try to find an open local port if none specified
            # (Logic borrowed from plotly.io._orca.find_open_port())
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 0))
            _, port = s.getsockname()
            s.close()
            self.port = port

    def show(self, app, *args, **kwargs):
        self._perform_show(0, app, *args, **kwargs)

    def _perform_show(self, tries, app, *args, **kwargs):
        jupyterlab_url = AppViewer._jupyterlab_url

        if jupyterlab_url is None:
            # Give up after ~5 seconds
            if tries > 50:
                raise IOError("""
Unable to communicate with the jupyterlab-dash JupyterLab extension.
Is this Python kernel running inside JupyterLab with the jupyterlab-dash
extension installed?

You can install the extension with:

$ jupyter labextension install jupyterlab-dash
""")
            # Otherwise, try again in another thread after a small delay
            args = (tries+1, app,) + args
            timer = Timer(0.1, self._perform_show, args=args, kwargs=kwargs)
            timer.daemon = True
            timer.start()
        else:
            def run(*args, **kwargs):
                # Serve App
                sys.stdout = self.stderr_queue
                sys.stderr = self.stderr_queue

                # Set pathname prefix for jupyter-server-proxy
                path = urlparse(jupyterlab_url).path
                app.config.update({
                    'requests_pathname_prefix': f'{path}proxy/{self.port}/'})

                app.run_server(debug=False, *args, **kwargs)

            # Terminate any existing server process
            self.terminate()

            # Give the OS a moment to free up the port before
            # telling Dash to use it again.  This duration was chosen to
            # work around errors when used on binder, and may need to be
            # adjusted in the future
            time.sleep(0.1)

            # precedence host and port
            launch_kwargs = {'host': self.host, 'port': self.port}
            launch_kwargs.update(kwargs)

            # Start new server process in separate process
            self.server_process = multiprocessing.Process(
                target=run, args=args, kwargs=launch_kwargs)

            self.server_process.daemon = True
            self.server_process.start()

            self._show_when_server_is_ready()

    def _show_when_server_is_ready(self):
        # Wait for server to start
        started = False
        retries = 0
        while not started and retries < 100:
            try:
                out = self.stderr_queue.queue.get(timeout=.1)
                try:
                    out = out.decode()
                except AttributeError:
                    pass

                if 'Running on' in out:
                    started = True
            except Empty:
                retries += 1
                pass

        if started:
            # Update front-end extension
            self._dash_comm.send({
                'type': 'show',
                'uid': self.uid,
                'port': self.port
            })
        else:
            # Failed to start development server
            raise ConnectionError('Unable to start Dash server')

    def terminate(self):
        if self.server_process:
            self.server_process.terminate()


# Register handler to process events sent from the
# front-end JupyterLab extension to the python kernel
@AppViewer._dash_comm.on_msg
def _recv(msg):
    msg_data = msg.get('content').get('data')
    msg_type = msg_data.get('type', None)
    if msg_type == 'url_response':
        AppViewer._jupyterlab_url = msg_data['url']


# If running in an ipython kernel,
# request that the front end extension send us the notebook server base URL
if IPython.get_ipython() is not None:
    AppViewer._dash_comm.send({
        'type': 'url_request'
    })
