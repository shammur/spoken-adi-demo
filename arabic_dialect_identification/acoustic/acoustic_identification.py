# -*- coding: utf-8 -*-

import os
import tensorflow as tf
import numpy as np
import soundfile as sf
import librosa

from io import BytesIO
import wave

# import nn_model as nn_model_foreval
try:
    from ..utils import nn_model as nn_model_foreval
except:
    from arabic_dialect_identification.utils import nn_model as nn_model_foreval


def cmvn_slide(feat, winlen=300, cmvn=False):  # feat : (length, dim) 2d matrix
    # function for Cepstral Mean Variance Nomalization

    maxlen = np.shape(feat)[0]
    new_feat = np.empty_like(feat)
    cur = 1
    leftwin = 0
    rightwin = winlen / 2

    # middle
    for cur in range(maxlen):
        cur_slide = feat[cur - leftwin:cur + rightwin, :]
        # cur_slide = feat[cur-winlen/2:cur+winlen/2,:]
        mean = np.mean(cur_slide, axis=0)
        std = np.std(cur_slide, axis=0)
        if cmvn == 'mv':
            new_feat[cur, :] = (feat[cur, :] - mean) / std  # for cmvn
        elif cmvn == 'm':
            new_feat[cur, :] = (feat[cur, :] - mean)  # for cmn
        if leftwin < winlen / 2:
            leftwin += 1
        elif maxlen - cur < winlen / 2:
            rightwin -= 1
    return new_feat


def feat_extract(y, sr, feat_type, n_fft_length=512, hop=160, vad=True, cmvn=False, exclude_short=500):
    # function for feature extracting


    #     filelist = np.loadtxt(filename,delimiter='\t',dtype='string',usecols=(0))
    #     utt_label = np.loadtxt(filename,delimiter='\t',dtype='int',usecols=(1))

    feat = []
    utt_shape = []
    new_utt_label = []
    # read audio input
    # y, sr = librosa.core.load(wavname, sr=16000, mono=True, dtype='float')

    # extract feature
    if feat_type == 'melspec':
        Y = librosa.feature.melspectrogram(y, sr, n_fft=n_fft_length, hop_length=hop, n_mels=40, fmin=133, fmax=6955)
    elif feat_type == 'mfcc':
        Y = librosa.feature.mfcc(y, sr, n_fft=n_fft_length, hop_length=hop, n_mfcc=40, fmin=133, fmax=6955)
    Y = Y.transpose()

    # Simple VAD based on the energy
    if vad:
        E = librosa.feature.rmse(y, frame_length=n_fft_length, hop_length=hop, )
        threshold = np.mean(E) / 2 * 1.04
        vad_segments = np.nonzero(E > threshold)
        if vad_segments[1].size != 0:
            Y = Y[vad_segments[1], :]

    # exclude short utterance under "exclude_short" value
    if exclude_short == 0 or (Y.shape[0] > exclude_short):
        if cmvn:
            Y = cmvn_slide(Y, 300, cmvn)
        feat.append(Y)
        utt_shape.append(np.array(Y.shape))
        #             new_utt_label.append(utt_label[index])
        # sys.stdout.write('%s\r' % index)
        # sys.stdout.flush()



    tffilename = feat_type + '_fft' + str(n_fft_length) + '_hop' + str(hop)
    if vad:
        tffilename += '_vad'
    if cmvn == 'm':
        tffilename += '_cmn'
    elif cmvn == 'mv':
        tffilename += '_cmvn'
    if exclude_short > 0:
        tffilename += '_exshort' + str(exclude_short)

    return feat, new_utt_label, utt_shape, tffilename  # feat : (length, dim) 2d matrix

# Feature extraction configuration
FEAT_TYPE = 'mfcc'
N_FFT = 512
HOP = 160
VAD = True
CMVN = 'm'
EXCLUDE_SHORT=0

# extracting mfcc for input wavfile
# FILENAME = ['./data/EGY003100.wav']
langList = [u'EGY', u'GLF', u'LAV', u'MSA', u'NOR']

# Variable Initialization
softmax_num = 5

x = tf.placeholder(tf.float32, [None,None,40])
y = tf.placeholder(tf.int32, [None])
s = tf.placeholder(tf.int32, [None,2])

emnet_validation = nn_model_foreval.nn(x,y,y,s,softmax_num)
# sess = tf.InteractiveSession()
sess2 = tf.Session()
saver2 = tf.train.Saver()
# tf.initialize_all_variables().run()
sess2.run(tf.global_variables_initializer())

### Loading neural network
current_directory = os.path.dirname(os.path.abspath(__file__))
model_directory = os.path.join(current_directory, 'model')
model_path = os.path.join(model_directory, 'model910000.ckpt')
saver2.restore(sess2, model_path)

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def dialect_estimation(bytesIO_buffer):
    data, sample_rate = sf.read(bytesIO_buffer)
    feat, utt_label, utt_shape, tffilename = feat_extract(data, sample_rate, FEAT_TYPE,N_FFT,HOP,VAD,CMVN,EXCLUDE_SHORT)
    likelihood= emnet_validation.o1.eval({x:feat, s:utt_shape, }, session=sess2)

    probabilities = softmax(likelihood.ravel().tolist())

    return dict(zip(langList, probabilities))

    # dialect_index = np.argmax(likelihood)
    # if dialect_index == 0:
    #     return ' [Egytion]'
    # elif dialect_index == 1:
    #     return ' [Gulf]'
    # elif dialect_index == 2:
    #     return ' [Levantine]'
    # elif dialect_index == 3:
    #     return ' [Modern Standard Arabic]'
    # elif dialect_index == 4:
    #     return ' [North African]'
    # else:
    #     return ' [I don\'t know that dialect]'


if __name__=='__main__':
    raw_file = os.path.join(r'/var/spool/asr/nnet3sac', 'c442bfff-9e1c-4af5-b7af-d22c0dd8988b' + '.raw')
    raw_file_size = os.path.getsize(raw_file)

    # if it the audio file has more than 20 SECs which is 1024*600
    if raw_file_size >= 614400:
        buffer = BytesIO()
        wave_file = wave.open(buffer, 'w')
        wave_file.setnchannels(1)
        wave_file.setframerate(16000)
        wave_file.setsampwidth(2)

        file_object = open(raw_file, 'rb', os.O_NONBLOCK)

        file_object.seek(-1024 * 600, 2)
        wave_file.writeframes(file_object.read())
        wave_file.close()
        buffer.flush()
        buffer.seek(0)

    #print dialect_estimation(buffer)