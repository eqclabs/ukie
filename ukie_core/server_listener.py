from .server import MessageSender
import threading
import json
from time import sleep


class FakeEpc():
    def __init__(self):
        pass

    def setDC(self):
        return 'successfully set to DC mode on alice'


class ServerListener():

    def __init__(self, hostname, local_name, remote_name):
        self.hostname = hostname
        self.local_name = local_name
        self.remote_name = remote_name
        self.instruments = {}
        self.messenger = MessageSender(self.local_name, self.hostname)
        self.retrieve_thread = threading.Thread(
            name='retrieve',
            target=self._retrieve_messages)
        self.retrieve_thread.start()

    def _send_message(self, message):
        return self.messenger.send_message(self.remote_name, message)

    def _retrieve_messages(self):
        while True:
            messages = [json.loads(message)
                        for message in self.messenger.retrieve_messages()]
            for message in messages:
                print('executing message')
                self.execute_message(message)
                del message
            sleep(0.01)

    def execute_message(self, message: dict):
        print(message)
        instrument_name = message['instrument']
        function_name = message['function']
        args = message['args']
        kwargs = message['kwargs']
        instrument = self.instruments[instrument_name]
        function = getattr(instrument, function_name)

        reply = {
            'instrument': instrument_name,
            'function': function_name,
            'response': function(*args, **kwargs)
        }

        print(self._send_message(json.dumps(reply)))


if __name__ == '__main__':
    sl = ServerListener(
        'https://king-prawn-app-yv9q2.ondigitalocean.app', 'alice', 'bob')
    sl.instruments['epc'] = FakeEpc()
