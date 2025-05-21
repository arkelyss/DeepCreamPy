import tensorflow as tf
from tensorflow.keras import layers
from ops import *
import math

# Utility: Reflect padding for TF2
class ReflectPad2D(tf.keras.layers.Layer):
    def __init__(self, padding):
        super().__init__()
        self.padding = padding

    def call(self, x):
        return tf.pad(x, [[0, 0], [self.padding, self.padding], [self.padding, self.padding], [0, 0]], mode='REFLECT')


# Refactored conv block
class ConvNN(tf.keras.Model):
    def __init__(self, dims1, dims2, k_size=3):
        super().__init__()
        self.pad1 = ReflectPad2D(1)
        self.conv1 = layers.Conv2D(dims1, (k_size, k_size), padding='valid', activation='elu')
        self.pad2 = ReflectPad2D(1)
        self.conv2 = layers.Conv2D(dims2, (k_size, k_size), padding='valid', activation='elu')

    def call(self, x, size1, size2):
        x = self.pad1(x)
        x = self.conv1(x)
        x = self.pad2(x)
        x = self.conv2(x)
        return tf.image.resize(x, (size1, size2), method='nearest')


# Refactored Encoder
class Encoder(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.pad1 = ReflectPad2D(2)
        self.conv1 = layers.Conv2D(32, (5, 5), padding='valid')

        self.pad2 = ReflectPad2D(1)
        self.conv2 = layers.Conv2D(64, (3, 3), strides=(2, 2), padding='valid')

        self.pad3 = ReflectPad2D(1)
        self.conv3 = layers.Conv2D(64, (3, 3), padding='valid')

        self.pad4 = ReflectPad2D(1)
        self.conv4 = layers.Conv2D(128, (3, 3), strides=(2, 2), padding='valid')

        self.pad5 = ReflectPad2D(1)
        self.conv5 = layers.Conv2D(128, (3, 3), padding='valid')

        self.pad6 = ReflectPad2D(1)
        self.conv6 = layers.Conv2D(256, (3, 3), strides=(2, 2), padding='valid')

        self.dilated = []
        for rate, pad in zip([2, 4, 8, 16], [2, 4, 8, 16]):
            self.dilated.append((ReflectPad2D(pad), layers.Conv2D(256, (3, 3), dilation_rate=rate, padding='valid')))

    def call(self, x):
        x = tf.nn.elu(self.conv1(self.pad1(x)))
        x = tf.nn.elu(self.conv2(self.pad2(x)))
        x = tf.nn.elu(self.conv3(self.pad3(x)))
        x = tf.nn.elu(self.conv4(self.pad4(x)))
        x = tf.nn.elu(self.conv5(self.pad5(x)))
        x = tf.nn.elu(self.conv6(self.pad6(x)))
        for pad, conv in self.dilated:
            x = tf.nn.elu(conv(pad(x)))
        return x


# You can now instantiate and use:
# encoder = Encoder()
# result = encoder(input_tensor)

# Let me know when you're ready for the refactor of `decoder`, `discriminator`, or the `contextual_block` functions.
