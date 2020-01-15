# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:19:28 2020

@author: Lnofeisone
"""

import tensorflow as tf

#first, create a TF constant

const = tf.constant(2.0, name = 'constant')

#create TF variables
b = tf.Variable(2.0, name = 'b')
c = tf.Variable(1.0, name = 'c')


#if you run everything above, the variables haven't been declared...yet
#try running the command below and you'll see that Python declares variables

exampleVariable = 5 #notice how this is now a variable

d = tf.add(b, c, name = 'd')
e = tf.add(c, const, name = 'e')
a = tf.multiply(d, e, name = 'a')

# setup the variable initialisation
init_op = tf.Variable

#create TF variable
W = tf.Variable(tf.ones(shape=(2, 2)), name = 'W')
b = tf.Variable(tf.zeros(shape=(2)), name = 'b')

@tf.function
def forward(x):
    return W*x+b

out_a = forward([1, 0])
print(out_a)