# -*- coding: utf-8 -*-  
import numpy as np  
import tensorflow as tf  
import cv2  
import os  
import random  
import time  
  
number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  
t = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

char_set = []
for i in t:
    char_set.append(i)
for i in number:
    char_set.append(i)
# 图像大小  
IMAGE_HEIGHT = 60  
IMAGE_WIDTH = 160  
MAX_CAPTCHA = 8

CHAR_SET_LEN = len(char_set)  
  
X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT * IMAGE_WIDTH])  
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA * CHAR_SET_LEN])  
keep_prob = tf.placeholder(tf.float32)  # dropout  
  
# 定义CNN  
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):  
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])  
  
    # 3 conv layer  
    w_c1 = tf.Variable(w_alpha * tf.random_normal([3, 3, 1, 32]))  
    b_c1 = tf.Variable(b_alpha * tf.random_normal([32]))  
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))  
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  
    conv1 = tf.nn.dropout(conv1, keep_prob)  
  
    w_c2 = tf.Variable(w_alpha * tf.random_normal([3, 3, 32, 64]))  
    b_c2 = tf.Variable(b_alpha * tf.random_normal([64]))  
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))  
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  
    conv2 = tf.nn.dropout(conv2, keep_prob)  
  
    w_c3 = tf.Variable(w_alpha * tf.random_normal([3, 3, 64, 64]))  
    b_c3 = tf.Variable(b_alpha * tf.random_normal([64]))  
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))  
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  
    conv3 = tf.nn.dropout(conv3, keep_prob)  
  
    # Fully connected layer  
    w_d = tf.Variable(w_alpha * tf.random_normal([8 * 20 * 64, 1024]))  
    b_d = tf.Variable(b_alpha * tf.random_normal([1024]))  
    dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])  
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))  
    dense = tf.nn.dropout(dense, keep_prob)  
  
    w_out = tf.Variable(w_alpha * tf.random_normal([1024, MAX_CAPTCHA * CHAR_SET_LEN]))  
    b_out = tf.Variable(b_alpha * tf.random_normal([MAX_CAPTCHA * CHAR_SET_LEN]))  
    out = tf.add(tf.matmul(dense, w_out), b_out)  
    # out = tf.nn.softmax(out)  
    return out  
  
# 向量转回文本  
def vec2text(vec):  
    char_pos = vec.nonzero()[0]  
    text = []  
    for i, c in enumerate(char_pos):  
        char_at_pos = i  # c/63  
        char_idx = c % CHAR_SET_LEN  
        if char_idx < 10:  
            char_code = char_idx + ord('0')  
        elif char_idx < 36:  
            char_code = char_idx - 10 + ord('A')  
        elif char_idx < 62:  
            char_code = char_idx - 36 + ord('a')  
        elif char_idx == 62:  
            char_code = ord('_')  
        else:  
            raise ValueError('error')  
        text.append(chr(char_code))  
    return "".join(text)  
  
def predict_captcha(captcha_image):  
    output = crack_captcha_cnn()  
  
    saver = tf.train.Saver()  
    with tf.Session() as sess:  
        saver.restore(sess, tf.train.latest_checkpoint('.'))  
  
        predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)  
        text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})  
  
        text = text_list[0].tolist()  
        vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)  
        i = 0  
        for n in text:  
            vector[i * CHAR_SET_LEN + n] = 1  
            i += 1  
        return vec2text(vector)  
  
#单张图片预测  
image = np.float32(cv2.imread('./ceshi_data/fcve2.jpg', 0))  
text = 'fcve2'  
image = image.flatten() / 255  
predict_text = predict_captcha(image)
print("正确: {0}  预测: {1}".format(text, predict_text))  