"""Neural style transfer with Keras.

# References
    - [A Neural Algorithm of Artistic Style](http://arxiv.org/abs/1508.06576)
"""

from __future__ import print_function
from training import Model
from training_record import TrainingRecorder
from img_prep import img_in, img_save, preprocess_image, grey_image
from settings import content_path, style_path, loss_set, result_dir

# load content and style image
content, style = img_in(content_path, style_path)

tr = TrainingRecorder(loss_set, result_dir, img_save, '.png')

idx = tr.get_head() - 1
if idx >= 0:
    x = preprocess_image(tr.get_name(idx))
else:
    x = grey_image()

idx += 1

model = Model(content, style, x)

try:
    for i in range(idx, 10000):
        print('Start of iteration', i)
        loss, result = model.update()
        # save current generated image
        tr.record(i, loss, result)

except KeyboardInterrupt:
    tr.export_file()
