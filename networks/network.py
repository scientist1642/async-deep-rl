# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
from . import layers


class Network(object):

    def __init__(self, conf):
        """ Initialize hyper-parameters, set up optimizer and network 
        layers common across Q and Policy/V nets. """

        self.name = conf['name']
        self.num_actions = conf['num_act']
        self.arch = conf['args'].arch
        self.batch_size = conf['args'].batch_size
        self.optimizer_type = conf['args'].opt_type
        self.optimizer_mode = conf['args'].opt_mode
        self.clip_loss_delta = conf['args'].clip_loss_delta
        self.clip_norm = conf['args'].clip_norm
        self.clip_norm_type = conf['args'].clip_norm_type
        self.input_shape = conf['input_shape']

        with tf.name_scope(self.name):
            self.selected_action_ph = tf.placeholder(
                'float32', [self.batch_size, self.num_actions], name='selected_action')
                
            if self.arch == 'FC':
                self.input_ph = tf.placeholder('float32', [self.batch_size]+self.input_shape+[4], name='input')
                self.w1, self.b1, self.o1 = layers.fc('fc1', layers.flatten(self.input_ph), 40, activation='relu')
                self.w2, self.b2, self.o2 = layers.fc('fc2', self.o1, 40, activation='relu')
                self.ox = self.o2
            elif self.arch == 'NIPS':
                self.input_ph = tf.placeholder('float32',[self.batch_size, 84, 84, 4], name='input')
                self.w1, self.b1, self.o1 = layers.conv2d('conv1', self.input_ph, 16, 8, 4, 4)
                self.w2, self.b2, self.o2 = layers.conv2d('conv2', self.o1, 32, 4, 16, 2)
                self.w3, self.b3, self.o3 = layers.fc('fc3', layers.flatten(self.o2), 256, activation='relu')
                self.ox = self.o3
            elif self.arch == 'NATURE':
                self.input_ph = tf.placeholder('float32',[self.batch_size, 84, 84, 4], name='input')
                self.w1, self.b1, self.o1 = layers.conv2d('conv1', self.input_ph, 32, 8, 4, 4)
                self.w2, self.b2, self.o2 = layers.conv2d('conv2', self.o1, 64, 4, 32, 2)
                self.w3, self.b3, self.o3 = layers.conv2d('conv3', self.o2, 64, 3, 64, 1)
                self.w4, self.b4, self.o4 = layers.fc('fc4', layers.flatten(self.o3), 512, activation='relu')
                self.ox = self.o4
            else:
                raise Exception('Invalid architecture `{}`'.format(self.arch))

    
        
