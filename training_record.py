import json
import time
import re
import os
from os import path, listdir
import requests, json

class TrainingRecorder(object):
    def __init__(self, loss_set, output_dir, saver, ext=None, axis='iteration'):
        self.start_time = time.time()
        self.last_time = self.start_time

        self.loss_set = loss_set
        self.loss_label = list(list(zip(*loss_set))[0])
        self.loss_label.insert(0, 'total')  # add total loss
        self.losses = dict([(n, []) for n in self.loss_label])

        self.outputs = []

        self.output_dir = output_dir
        if not path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.ext = ext
        self.saver = saver

        self.axis = axis

    def get_head(self):
        """
        Get the index which we should start from
        :return:
        """
        # idx = -1
        with open('result.json', 'r') as f:
            myjson = json.load(f)
            if len(myjson['output']) == 0:
                return 1
            self.outputs = myjson['output']
            self.losses = myjson['loss']
            it = myjson['output'][-1]
            return it[0]+1

    def reset(self):
        """
        Reset start_time
        :return:
        """
        self.start_time = time.time()

    def record(self, iteration, losses, output):
        """
        Record it.
        :param iteration: current iteration
        :param losses: current loss
        :param output: current output
        :return:
        """
        nowtime = time.time()
        print('Iteration %d completed in %fs' % (iteration, nowtime - self.last_time))
        timeoffset = nowtime - self.start_time
        self.last_time = nowtime

        axis = iteration if self.axis == 'iteration' else timeoffset
        # Append loss
        for t, v in zip(self.loss_label, losses):
            self.losses[t].append([axis, float(v)])
            print('%s loss value: %e' % (t, v))

        # Append output
        output_path = self.get_name(iteration)
        self.saver(output, output_path)
        self.outputs.append([axis, output_path])
        print("results saved at %s \n" % output_path)
        myjson = {
            'losses': [float(loss) for loss in losses],
            'loss_label': self.loss_label,
            'output': [axis, output_path],
            'iter': iteration
        }
        requests.post('http://localhost:8000/record', None, myjson)


    def get_name(self, idx):
        """
        Get the path to file according to the index
        :param idx: current index
        :return: Path to file
        """
        return path.join(self.output_dir, str(idx)) + (self.ext if self.ext else '')

    def export(self):
        """
        Export recording as json string
        :return: json for recording
        """
        return json.dumps({'loss': self.losses, 'output': self.outputs})

    def export_file(self):
        """
        Export recording to file `$output_dir.json`
        :return:
        """
        with open('result.json', 'w') as f:
            return json.dump({'loss': self.losses, 'output': self.outputs}, f)
