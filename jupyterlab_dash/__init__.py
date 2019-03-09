import multiprocessing
import socket
import uuid
from queue import Empty
from urllib.parse import urlparse
import sys

from ipykernel.comm import Comm
from notebook import notebookapp

class StdErrorQueue(object):
    def __init__(self):
        self.queue = multiprocessing.Queue()

    def write(self, v):
        self.queue.put(v)

    def flush(self):
        sys.__stderr__.flush()


class AppViewer(object):
    _dash_comm = Comm(target_name='dash_viewer')

    def __init__(self, host='localhost', port=8050):
        self.server_process = None
        self.uid = str(uuid.uuid4())
        self.host = host
        self.port = port
        self.stderr_queue = StdErrorQueue()

    def show(self, app, *args, **kwargs):
        def run(*args, **kwargs):
            # Serve App
            sys.stdout = self.stderr_queue
            sys.stderr = self.stderr_queue

            # Set pathname prefix for jupyter-server-proxy
            url = next(notebookapp.list_running_servers())['url']

            path = urlparse(url).path
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
