# -*- coding: utf-8 -*-
from . import layers
import tensorflow as tf
from .network import Network


class QNetwork(Network):

    def __init__(self, conf):
        """ Set up remaining layers, loss function, gradient compute and apply 
        ops, network parameter synchronization ops, and summary ops. """

        super(QNetwork, self).__init__(conf)
                
        with tf.name_scope(self.name):
        
            self.target_ph = tf.placeholder('float32', [None], name='target')
            self.w_out, self.b_out, self.output_layer = layers.fc('fc_out', self.ox, self.num_actions, activation="linear")

            self.params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)

            # Loss
            # Multiply the output of the network by a one hot vector 1 for the 
            # executed action. This will make the loss due to non-selected 
            # actions to be zero.
            if "target" not in self.name:
                output_selected_action = tf.reduce_sum(tf.multiply(self.output_layer, 
                                                              self.selected_action_ph), axis=1)
                
                diff = tf.subtract(self.target_ph, output_selected_action)
            
                # DEFINE HUBER LOSS
                if self.clip_loss_delta > 0:
                    quadratic_term = tf.minimum(tf.abs(diff), self.clip_loss_delta)
                    linear_term = tf.abs(diff) - quadratic_term
                    self.loss = tf.nn.l2_loss(quadratic_term) + self.clip_loss_delta*linear_term
                else:
                    self.loss = tf.nn.l2_loss(diff)
                      
                # Operations to compute gradients
                with tf.control_dependencies(None):
                    grads = tf.gradients(self.loss, self.params)
                    
                    # This is not really an operation, but a list of gradient Tensors 
                    # When calling run() on it, the value of those Tensors 
                    # (i.e., of the gradients) will be calculated.
                    self.clipped_grad_hist_op = None
                    if self.clip_norm_type == 'ignore':
                        self.get_gradients = grads
                    elif self.clip_norm_type == 'global':
                        self.get_gradients = tf.clip_by_global_norm(grads, self.clip_norm)[0]
                    elif self.clip_norm_type == 'avg':
                        self.get_gradients = tf.clip_by_average_norm(grads, self.clip_norm)[0]
                    elif self.clip_norm_type == 'local':
                        self.get_gradients = [
                            tf.clip_by_norm(g, self.clip_norm) for g in grads
                        ]

            # Placeholders for shared memory vars
            self.params_ph = []
            for p in self.params:
                self.params_ph.append(tf.placeholder(tf.float32, 
                    shape=p.get_shape(), 
                    name="shared_memory_for_{}".format(
                        (p.name.split("/", 1)[1]).replace(":", "_"))))
            
            # Ops to sync net with shared memory vars
            self.sync_with_shared_memory = []
            for i in range(len(self.params)):
                self.sync_with_shared_memory.append(
                    self.params[i].assign(self.params_ph[i]))

