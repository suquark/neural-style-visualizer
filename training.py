from __future__ import print_function
from keras.optimizers import Nadam
import keras.backend as K
from settings import img_height, img_width, input_shape, learning_rate
from settings import loss_set, content_feature_layers, style_feature_layers
from vgg16_cnnonly_model import set_model_input, model_with_input
import requests


def gram_matrix(x):
    """
    the gram matrix of an image tensor (feature-wise outer product)
    :param x: The tensor contains image features
    :return: A gram matrix
    """
    if K.ndim(x) == 4:
        x = x[0, :, :, :]
    assert K.ndim(x) == 3
    features = K.batch_flatten(x)
    gram = K.dot(features, K.transpose(features))
    return gram


def style_loss(style, combination):
    """
    To calculate style loss from gram matrix
    :param style: gram matrix from the style image
    :param combination: gram matrix from the generated image
    :return: A loss represent diffs between 2 gram matrices
    """
    channels = 3
    size = img_width * img_height
    return K.sum(K.square(style - combination)) / (4. * (channels ** 2) * (size ** 2))


class Model(object):
    def __init__(self, content, style, x):
        self.content_features = {}
        self.style_features = {}
        self.model = None
        # evaluate features of content and style images
        print("Pre-evaluate features...")
        requests.post('http://localhost:8000/setmsg', None,
                              {'msg': "Pre-evaluate features..."})
        # global msg
        # msg = "Pre-evaluate features..."
        self.gen_model(K.placeholder(input_shape))
        self.f_output = K.function([self.input_tensor], list(self.outputs_dict.values()))
        self.writedown_content_feature(content)
        self.writedown_style_feature(style)

        # training model
        self.gen_model(K.variable(x))
        self.optimizer = Nadam(lr=learning_rate)
        self.compile()

    def set_lr(self, learning_rate):
        """
        set the learning rate of the optimizer
        :param learning_rate: lerning rate pass to the optimizer
        :return:
        """
        # self.optimizer.lr.set_value(learning_rate)
        K.set_value(self.optimizer.lr, learning_rate)
        print('learning rate = {}'.format(learning_rate))
        requests.post('http://localhost:8000/setmsg', None,
                              {'msg': 'set learning rate to {}'.format(learning_rate)})
        # global msg
        # msg = 'learning rate = {}'.format(learning_rate)

    def gen_model(self, x):
        """
        Generate a VGG-19 model with certain inputs
        :param x: Input (numpy array)
        :return: A VGG-19 model
        """
        self.model = model_with_input(x)
        self.layers_dict = dict([(layer.name, layer) for layer in self.model.layers])
        self.outputs_dict = dict([(layer.name, layer.output) for layer in self.model.layers])
        self.inputs_dict = dict([(layer.name, layer.input) for layer in self.model.layers])
        self.input_tensor = x

    def get_feature(self, x):
        return dict(zip(self.outputs_dict.keys(), self.f_output([x])))

    def writedown_content_feature(self, content):
        # work out and keep content features
        outputs = self.get_feature(content)
        for layer_name in content_feature_layers:
            self.content_features[layer_name] = outputs[layer_name]

    def writedown_style_feature(self, style):
        # work out and keep style features
        outputs = self.get_feature(style)
        for layer_name in style_feature_layers:
            self.style_features[layer_name] = K.eval(gram_matrix(K.variable(outputs[layer_name])))

    def get_style_loss(self):
        """
        The "style loss" is designed to maintain the style of the reference image in the generated image.
        It is based on the gram matrices (which capture style) of feature maps from the style reference image
        and from the generated image
        :return: style loss
        """
        loss = K.variable(0.)
        for layer_name in style_feature_layers:
            style_features = K.variable(self.style_features[layer_name])
            combination_features = gram_matrix(self.outputs_dict[layer_name])
            loss += style_loss(style_features, combination_features)
        loss /= len(style_feature_layers)
        return loss

    def get_content_loss(self):
        """
        content loss, designed to maintain the "content" of the base image in the generated image
        :return: content loss
        """
        loss = K.variable(0.)
        for layer_name in content_feature_layers:
            content_features = K.variable(self.content_features[layer_name])
            combination_features = self.outputs_dict[layer_name]
            loss += K.sum(K.square(combination_features - content_features))
        loss /= len(content_feature_layers)
        return loss

    def total_variation_loss(self):
        """
        Total variation loss, designed to keep the generated image locally coherent
        :return: total variation loss
        """
        x = self.input_tensor
        assert K.ndim(x) == 4
        a = K.square(x[:, :, :img_width - 1, :img_height - 1] - x[:, :, 1:, :img_height - 1])
        b = K.square(x[:, :, :img_width - 1, :img_height - 1] - x[:, :, :img_width - 1, 1:])
        return K.sum(K.pow(a + b, 1.25))

    def get_loss(self):
        """
        Get all loss and corresponding weights
        :return: [loss1,...],[weight1,...]
        """
        loss_table = [self.get_content_loss(), self.get_style_loss(), self.total_variation_loss()]
        loss_weights = list(zip(*loss_set))[1]
        # loss_weights = [content_weight, style_weight, total_variation_weight]
        return loss_table, loss_weights

    def compile(self):
        """
        Defines the way to calculate loss and do optimization
        :return: None
        """
        # global msg
        print("Generate loss and grad...")
        requests.post('http://localhost:8000/setmsg', None,
                              {'msg': "Generate loss and grad..."})
        # msg = "Generate loss and grad..."
        losses = [l * w for l, w in zip(*self.get_loss())]
        total_loss = sum(losses)

        metrics = [total_loss] + losses
        constraints = []
        # constraints = [lambda x: K.clip(x, 0., 255.)]
        training_updates = self.optimizer.get_updates([self.inputs_dict['input']], constraints, total_loss)
        # returns loss and metrics. Updates weights at each call.
        self.train_function = K.function([], metrics, updates=training_updates)

    def update(self):
        """
        Step the optimization process
        :return: Info about loss and iteration result
        """
        return self.train_function([]), K.eval(self.inputs_dict['input'])
