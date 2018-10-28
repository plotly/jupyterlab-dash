import multiprocessing
import uuid
from ipykernel.comm import Comm


class AppViewer(object):
    _dash_comm = Comm(target_name='dash_viewer')

    def __init__(self, port=8050):
        self.server_process = None
        self.uid = str(uuid.uuid4())
        self.port = port

    def show(self, app):
        def run():
            # Serve App
            app.run_server(debug=False, port=self.port)

        # Terminate any existing server process
        self.terminate()

        # Start new server process in separate process
        self.server_process = multiprocessing.Process(target=run)
        self.server_process.start()

        # Update front-end extension
        self._dash_comm.send({
            'type': 'show',
            'uid': self.uid,
            'url': 'http://localhost:{}'.format(self.port)
        })

    def terminate(self):
        if self.server_process:
            self.server_process.terminate()
