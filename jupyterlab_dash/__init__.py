import multiprocessing
import socket
import uuid
from queue import Empty

from ipykernel.comm import Comm
import sys


class StdErrorQueue(object):
    def __init__(self):
        self.queue = multiprocessing.Queue()

    def write(self, v):
        self.queue.put(v)

    def flush(self):
        sys.__stderr__.flush()


class AppViewer(object):
    _dash_comm = Comm(target_name='dash_viewer')

    def __init__(self, host='127.0.0.1', port=8050, url=None):
        self.server_process = None
        self.uid = str(uuid.uuid4())
        self.host = host
        self.port = port
        self.url = url
        self.stderr_queue = StdErrorQueue()

    def show(self, app):
        def run():
            # Serve App
            sys.stdout = self.stderr_queue
            sys.stderr = self.stderr_queue
            app.run_server(debug=False, host=self.host, port=self.port)

        # Terminate any existing server process
        self.terminate()

        # Start new server process in separate process
        self.server_process = multiprocessing.Process(target=run)
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
            if self.url is None:
                hostname = socket.getfqdn() if self.host != '127.0.0.1' and self.host != 'localhost' else self.host
                self._dash_comm.send({
                    'type': 'show',
                    'uid': self.uid,
                    'url': 'http://{}:{}'.format(hostname, self.port)
                })
            else:
                self._dash_comm.send({
                    'type': 'show',
                    'uid': self.uid,
                    'url': self.url
                })

        else:
            # Failed to start development server
            raise ConnectionError('Unable to start Dash server')

    def terminate(self):
        if self.server_process:
            self.server_process.terminate()
