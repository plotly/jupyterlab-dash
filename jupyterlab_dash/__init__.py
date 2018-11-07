import multiprocessing
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

    def __init__(self, port=8050):
        self.server_process = None
        self.uid = str(uuid.uuid4())
        self.port = port
        self.stderr_queue = StdErrorQueue()

    def show(self, app):
        def run():
            # Serve App
            sys.stdout = self.stderr_queue
            sys.stderr = self.stderr_queue
            app.run_server(debug=False, port=self.port)

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
            self._dash_comm.send({
                'type': 'show',
                'uid': self.uid,
                'url': 'http://localhost:{}'.format(self.port)
            })
        else:
            # Failed to start development server
            raise ConnectionError('Unable to start Dash server')

    def terminate(self):
        if self.server_process:
            self.server_process.terminate()
