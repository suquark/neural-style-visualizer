from __future__ import print_function
import os
import sys

import multiprocessing
from start_training import start_training

import json
import uuid
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.escape import json_decode
from tornado.concurrent import Future
from tornado import gen

__author__ = 'xymeow', 'suquark'

# TODO: show training messages on the front end

label = None

start = False
trained = False
stop = False
lr = 1.0


# use long polling to update the training results
# I copied these codes from tornado/demo/chat
class MessageBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = []
        self.cache_size = 200

    def wait_for_messages(self, cursor=None):
        # Construct a Future to return to our caller.  This allows
        # wait_for_messages to be yielded from a coroutine even though
        # it is not a coroutine itself.  We will set the result of the
        # Future when results are available.
        result_future = Future()
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                result_future.set_result(self.cache[-new_count:])
                return result_future
        self.waiters.add(result_future)
        return result_future

    def cancel_wait(self, future):
        self.waiters.remove(future)
        # Set an empty result to unblock any coroutines waiting.
        future.set_result([])

    def new_messages(self, messages):
        # logging.info("Sending new message to %r listeners", len(self.waiters))
        for future in self.waiters:
            future.set_result(messages)
        self.waiters = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


record_pool = MessageBuffer()


class MainHandler(RequestHandler):
    def get(self):
        self.render('index.html', json='/json')

    def post(self):
        json = json_decode(self.request.body)
        self.render('index.html', json=json)


class RecordHandler(RequestHandler):
    def post(self):
        json_dict = json_decode(self.request.body)
        print(self.request.body)

        myjson = {
            'id': str(uuid.uuid4()),
            'json': json_dict
        }

        record_pool.new_messages([myjson])


class PullRecordHandler(RequestHandler):
    def get(self):
        return

    @gen.coroutine
    def post(self):
        cursor = self.get_argument("cursor", None)
        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        self.future = record_pool.wait_for_messages(cursor=cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))

    def on_connection_close(self):
        record_pool.cancel_wait(self.future)


class TrainHandler(RequestHandler):
    def get(self):
        global trained, start, label
        if not start:
            start = True
            trained = True
            multiprocessing.Process(target=start_training).start()
        elif trained:
            trained = False
        elif not trained:
            trained = True
        self.write(json.dumps(trained))


class StatusHandler(RequestHandler):
    def get(self):
        global trained
        status = 'training'
        if not trained and not stop:
            status = 'pause'
        if stop or not start:
            status = 'stop'
        self.write(status)


class StopHandler(RequestHandler):
    def get(self):
        global stop
        global start
        stop = True
        start = False


class PictureHandler(RequestHandler):
    def get(self):
        print(self.get_argument('path'))
        p = open(self.get_argument('path'), 'rb')
        self.write(p.read())
        p.close()


class InitJSONHandler(RequestHandler):
    def get(self):
        if os.path.exists(label + '.json'):
            with open(label + '.json', 'rb') as f:
                self.write(f.read())
        else:
            print('Record file not found.')
            self.write('{}')


class LearningRateHandler(RequestHandler):
    def get(self):
        global lr
        self.write(str(lr))

    def post(self):
        global lr
        # print(self.get_argument('lr'))
        lr = float(self.get_argument('lr'))
        print('set learnig rate to {}'.format(lr))


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = Application([
    (r"/", MainHandler),
    (r"/json", PullRecordHandler),
    (r"/stop", StopHandler),
    (r"/record", RecordHandler),
    (r"/status", StatusHandler),
    (r"/picture", PictureHandler),
    (r"/init", InitJSONHandler),
    (r"/lr", LearningRateHandler),
    (r"/train", TrainHandler)
], **settings)

if __name__ == "__main__":
    # assert len(sys.argv) > 1, 'You should give the name of this training'
    label = sys.argv[1] if len(sys.argv) > 1 else 'result'  # Which record would you like to take?
    application.listen(8000)
    IOLoop.instance().start()
