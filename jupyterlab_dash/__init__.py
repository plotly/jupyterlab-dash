import multiprocessing
import socket
import uuid
import retrying
from queue import Empty
from urllib.parse import urlparse
import sys

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

    def __init__(self, host='localhost', port=8050):
        self.server_process = None
        self.uid = str(uuid.uuid4())
        self.host = host
        self.port = port
        self.stderr_queue = StdErrorQueue()

    @staticmethod
    @retrying.retry(stop_max_delay=5000)
    def _get_or_wait_for_jupyterlab_url():
        if AppViewer._jupyterlab_url is None:
            raise ValueError('_jupyterlab_url is None')
        return AppViewer._jupyterlab_url

    @staticmethod
    def get_jupyterlab_url():
        try:
            return AppViewer._get_or_wait_for_jupyterlab_url()
        except ValueError as e:
            raise IOError("""
Unable to communicate with the jupyterlab-dash JupyterLab extension.
Is this Python kernel running inside JupyterLab with the jupyterlab-dash
extension installed?

You can install the extension with:

$ jupyter labextension install jupyterlab-dash
""")

    def show(self, app, *args, **kwargs):
        jupyterlab_url = AppViewer.get_jupyterlab_url()

        def run(*args, **kwargs):
            # Serve App
            sys.stdout = self.stderr_queue
            sys.stderr = self.stderr_queue

            # Set pathname prefix for jupyter-server-proxy
            path = urlparse(jupyterlab_url).path
            app.config.update({'requests_pathname_prefix': f'{path}proxy/{self.port}/'})
            
            app.run_server(debug=False, *args, **kwargs)

        # Terminate any existing server process
        self.terminate()

        # precedence host and port
        launch_kwargs = {'host': self.host, 'port': self.port}
        launch_kwargs.update(kwargs)

        # Start new server process in separate process
        self.server_process = multiprocessing.Process(target=run, args=args, kwargs=launch_kwargs)
        self.server_process.daemon = True
        self.server_process.start()

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
            hostname = launch_kwargs['host']
            resolved_host = socket.getfqdn() if hostname != '127.0.0.1' and hostname != 'localhost' else hostname
            self._dash_comm.send({
                'type': 'show',
                'uid': self.uid,
                'url': 'http://{}:{}'.format(resolved_host, launch_kwargs['port']),
                'port': launch_kwargs['port']
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


# Request that the front end extension send us the notebook server base URL
AppViewer._dash_comm.send({
    'type': 'url_request'
})
