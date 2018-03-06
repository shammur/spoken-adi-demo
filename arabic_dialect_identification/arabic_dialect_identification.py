# -*- coding: utf-8 -*-
import numpy as np
import tensorflow as tf
import codecs
import os

__author__ = 'Mohamed Eldesouki'
__date__ = '28 Nov 2017'

try:
   import cPickle as pickle
except:
   import pickle

import siamese_model_words as siamese_model

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.join(current_directory, os.pardir)
data_directory = os.path.join(parent_directory, "data")
model_directory = os.path.join(parent_directory, "model")


phoneMap_path = os.path.join(data_directory, 'phoneMap.pkl') #r'./data/phoneMap.pkl'
suwan_model = os.path.join(model_directory, 'model60400.ckpt') # r'./model/model60400.ckpt'
language_model_path = os.path.join(data_directory, 'lang_mean_words.npy') #r'./data/lang_mean_words.npy'

if __name__ == '__main__':
    phoneMap_path = os.path.join(data_directory, 'phoneMap.pkl') # r'../../data/phoneMap.pkl'
    suwan_model = os.path.join(model_directory, 'model60400.ckpt') # r'../../model/model60400.ckpt'
    language_model_path = os.path.join(data_directory, 'lang_mean_words.npy') #r'../../data/lang_mean_words.npy'

with codecs.open(phoneMap_path, mode='rb') as phf:
    phoneMap = pickle.load(phf)

langList = [u'EGY', u'GLF', u'LAV', u'MSA', u'NOR']
input_dim = 41657

# init variables
sess = tf.Session()

siamese = siamese_model.siamese(input_dim)
global_step = tf.Variable(0, trainable=False)
learning_rate = tf.train.exponential_decay(0.01, global_step,
                                           5000, 0.99, staircase=True)
train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(siamese.loss, global_step=global_step)
saver = tf.train.Saver()
sess.run(tf.global_variables_initializer())

saver.restore(sess, suwan_model)  # saver_folder+'/model'+str(RESTORE_STEP)+'.ckpt'

# utterance = "انا مقلتش كدا خالص إمبارح"
lang_mean_siam = np.load(language_model_path)

ar = u"\u0627\u0625\u0622\u0623\u0621\u0628\u062a\u062b\u062c\u062d\u062e\u062f\u0630\u0631\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063a\u0641\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u064a\u0649\u0629\u0624\u0626\u064e\u064b\u064f\u064c\u0650\u064d\u0652\u0651"
buck = u"A<|>'btvjHxd*rzs$SDTZEgfqklmnhwyYp&}aFuNiKo~"

a2b_translation_table = dict(zip(ar, buck))
b2a_translation_table = dict(zip(buck, ar))


def utf82buck(kdinput):
    return ''.join([a2b_translation_table.get(ch, ch) for ch in kdinput])


def buck2utf8(kdinput):
    return ''.join([b2a_translation_table.get(ch, ch) for ch in kdinput])

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def identify_dialect(utterance):
    # print '################  del',utterance, 'del  ###############'
    utterance_transliterated = utf82buck(utterance)
    utt_indxes = dict()
    # print '################  del', utterance_transliterated, 'del  ###############'
    utt_ft = np.zeros((1, input_dim), dtype='float32')

    for ngram in utterance_transliterated.strip().split():
        ngram_index = phoneMap.get(ngram, None)
        if not ngram_index:
            continue
        if ngram_index in utt_indxes.keys():
            utt_indxes[ngram_index] += 1
        else:
            utt_indxes[ngram_index] = 1
    else:
        if len(utt_indxes) != 0 and len(utterance_transliterated) != 0:
            for ph_idx, word_count in utt_indxes.items():
                utt_ft[0][ph_idx-1] = word_count
            utt_ft_siam = siamese.o1.eval( {siamese.x1: utt_ft},session=sess)
            utt_scores = lang_mean_siam.dot(utt_ft_siam.transpose())
            # hypo_lang = np.argmax(utt_scores, axis=0)
            # print repr(utterance)
            # return langList[hypo_lang.squeeze()]

            # convert from scores to probabilities for the purpose of visualization
            probabilities = softmax(utt_scores.ravel().tolist())
            probabilities[4] = probabilities[4] * 0.1
            # probabilities = softmax(probabilities)
            return dict(zip(langList, probabilities))

        else:
            return dict(zip(langList, [0, 0, 0, 0, 0]))


if __name__ == '__main__':
    u1 = u"AlErby >m Al>kvr mA$yyn ArtfAE tkAlyf Al$Hn ArtfAE tkAlyf AlmEArD >h ElY mstwY AlwTn AlErby <rtfAE >sEAr Al<ElAnAt"
    print buck2utf8(u1)
    dialect = identify_dialect(u1)
    print dialect