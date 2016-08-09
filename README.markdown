# Neural-Style Visualization

This project aims at visualize loss and other important metrics for analysis.

This project also implement an instance of neural-style, follows the idea of a keras example `keras/examples/neural_style_transfer.py`, 
but with a mostly different design.

Visualization is important and fun. It tells us what's going on.

## Requirements

- python 3
- keras
- tensorflow >= 0.9.0 / Theano
- h5py
- Pillow
- requests
- tornado 


 
## Usage

make sure you have the requirements above, or type this in your command line:

	sudo pip install -r requirements.txt

if you want to use tensorflow as backend, follow the [instruction](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/g3doc/get_started/os_setup.md) to install tensorflow first

then 

	python neural_style.py

now you can see the neural style board in `localhost:8000`

![](snapshots/neural_style_board.png)

## Loss analysis

For example, you may find an bad output

![](snapshots/1000.png)

after comparing the loss, you will found negative correlation between style loss and content loss(against the assumption of neural-style):

![](snapshots/200x200/2804.png)

so a very small picture may not be very suitable for neural-style task.

Here's a better result with nearly independent loss:

![](snapshots/340.png)
![](snapshots/992.png)

A very high learning rate:

![](snapshots/very-high-lr.png)

## Realtime watch 

![](snapshots/default.png)

## Headstart

You can stop your training at any time and continue at the last epoch.

## Realtime hyperparameter adjusting

You are free to adjust hyperparameter

## Speed

Using TensorFlow as backend.

CPU: about 30 seconds/iter on Macbook Pro

GPU: about 0.3 s/iter on an K20
