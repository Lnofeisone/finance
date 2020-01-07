# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 15:33:03 2020

@author: Lnofeisone
"""

import tensorflow as tf
import numpy as np

graph = tf.Graph() # creates a graph
#session = tf.compat.v1.InteractiveSession(graph = graph) # creates a session

x = tf.placeholder(shape = [ 1, 10], dtype = tf.float32, name = 'x')
tf.zeros(shape = [5], dtype = tf.float32)