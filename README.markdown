# Neural-Style Visualization

This project aims at visualize loss and other important metrics for analysis.

This project also implement an instance of neural-style, follows the idea of a keras example `keras/examples/neural_style_transfer.py`, 
but with a mostly different design.

Visualization is important and fun. It tells us what's going on.

## loss analysis

For example, you may find an bad output

![](1000.png)

after comparing the loss, you will found negative correlation between style loss and content loss(against the assumption of neural-style):

![](snapshots/200x200/2804.png)

so a very small picture may not be very suitable for neural-style task.

Here's a better result with nearly independent loss:

![](snapshots/200x200/340.png)
![](snapshots/200x200/992.png)

A very high learning rate:

![](snapshots/very-high-lr.png)

## realtime watch 

![](snapshots/default.png)

## headstart

You can stop your training at any time and continue at the last epoch.

## realtime hyperparameter adjusting

You are free to adjust hyperparameter


