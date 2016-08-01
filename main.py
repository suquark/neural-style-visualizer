"""Neural style transfer with Keras.

# References
    - [A Neural Algorithm of Artistic Style](http://arxiv.org/abs/1508.06576)
"""

from __future__ import print_function
from training import Model
from training_record import TrainingRecorder
from img_prep import img_in, img_save, preprocess_image, grey_image
from settings import content_path, style_path, loss_set, result_dir
import requests, time


# load content and style image
def start_training():

    content, style = img_in(content_path, style_path)

    tr = TrainingRecorder(loss_set, result_dir, img_save, '.png')

    idx = tr.get_head() - 1
    if idx >= 0:
        x = preprocess_image(tr.get_name(idx))
    else:
        x = grey_image()

    idx += 1

    model = Model(content, style, x)


    lst_lr = 1.0
    try:
        for i in range(idx, 10000):
            status = requests.get('http://localhost:8000/status').text
            lr = float(requests.get('http://localhost:8000/lr').text)
            if status == 'pause':
                i -= 1
                while True:
                    time.sleep(1)
                    status = requests.get('http://localhost:8000/status').text
                    if status != 'pause':
                        break
            elif status == 'training':
                print('Start of iteration', i)
                # msg = 'Start of iteration ' + str(i)
                if lst_lr != lr:
                    # if learning rate has changes, set a new lr for the optimizer
                    model.set_lr(lr)
                loss, result = model.update()
                # save current generated image
                tr.record(i, loss, result)
                lst_lr = lr
            elif status == 'stop':
                print('stop training and save weights into json file.')
                # msg = 'stop training and save weights into json file.'
                tr.export_file()
                break

    except KeyboardInterrupt:
        tr.export_file()
