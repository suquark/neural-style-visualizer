# dimensions of the generated picture.
img_width = 500
img_height = 500
input_shape = (None, 3, img_width, img_height)
# You can resize the picture later if necessary
assert img_height == img_width, 'Due to the use of the Gram matrix, width and height must match.'

# where the output should be released
result_dir = "result"

# The path of content & style image
content_path = 'inputs/content.png'
style_path = 'inputs/style.png'


learning_rate = 1.0
# layers which provide us with features
content_feature_layers = ['conv4_2']
style_feature_layers = ['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1']

# these are the weights of the different loss components
loss_set = [('content', 1.0),
            ('style', 50.0),
            ('total variation', 0.0)]
