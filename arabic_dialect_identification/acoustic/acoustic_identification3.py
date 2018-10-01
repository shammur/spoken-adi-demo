import os
import numpy as np
import librosa
import soundfile as sf
import tensorflow as tf
from io import BytesIO
import wave
import contextlib
try:
    from arabic_dialect_identification.acoustic.model2767000 import spk2vec_test24_you_trn_dev as nn_model_foreval
except:
    from arabic_dialect_identification.utils import spk2vec_test24_you_trn_dev as nn_model_foreval


langList = [u'EGY', u'GLF', u'LAV', u'MSA', u'NOR']
def cmvn_slide(feat, winlen=300, cmvn=False):  # feat : (length, dim) 2d matrix
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
    #     filelist = np.loadtxt(filename,delimiter='\t',dtype='string',usecols=(0))
    #     utt_label = np.loadtxt(filename,delimiter='\t',dtype='int',usecols=(1))

    feat = []
    utt_shape = []
    new_utt_label = []

    # for index, wavname in enumerate(filelist):
    # # read audio input
    # y, sr = librosa.core.load(wavname, sr=16000, mono=True, dtype='float')

    # extract feature
    if feat_type == 'melspec':
        Y = librosa.feature.melspectrogram(y, sr, n_fft=n_fft_length, hop_length=hop, n_mels=40, fmin=133,
                                           fmax=6955)
    elif feat_type == 'mfcc':
        Y = librosa.feature.mfcc(y, sr, n_fft=n_fft_length, hop_length=hop, n_mfcc=40, fmin=133, fmax=6955)
    elif feat_type == 'spec':
        Y = np.abs(librosa.core.stft(y, n_fft=n_fft_length, hop_length=hop, win_length=400))
    elif feat_type == 'logspec':
        Y = np.log(np.abs(librosa.core.stft(y, n_fft=n_fft_length, hop_length=hop, win_length=400)))
    elif feat_type == 'logmel':
        Y = np.log(librosa.feature.melspectrogram(y, sr, n_fft=n_fft_length, hop_length=hop, n_mels=40, fmin=133,
                                                  fmax=6955))

    Y = Y.transpose()

    # Simple VAD based on the energy
    if vad:
        E = librosa.feature.rmse(y, frame_length=n_fft_length, hop_length=hop, )
        threshold = np.mean(E) / 2 * 0.90
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
    #             sys.stdout.write('%s\r' % index)
    #             sys.stdout.flush()

    #        if index ==100:
    #            break

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
N_FFT = 400
HOP = 160
VAD = True
CMVN = 'mv'
EXCLUDE_SHORT=0
IS_BATCHNORM = False
IS_TRAINING = False
INPUT_DIM = 40

softmax_num = 5
x = tf.placeholder(tf.float32, [None,None,40])
y = tf.placeholder(tf.int32, [None])
s = tf.placeholder(tf.int32, [None,2])

emnet_validation = nn_model_foreval.nn(x,y,y,s,softmax_num,IS_TRAINING,INPUT_DIM,IS_BATCHNORM)
# sess = tf.InteractiveSession()
sess4 = tf.Session()
saver4 = tf.train.Saver()
# tf.initialize_all_variables().run()
sess4.run(tf.global_variables_initializer())

### Loading neural network
current_directory = os.path.dirname(os.path.abspath(__file__))
model_directory = os.path.join(current_directory, 'model')
model_path4 = os.path.join(model_directory, 'model2768000.ckpt-2768000')
saver4.restore(sess4,model_path4)


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def dialect_estimation(bytesIO_buffer):
    data, sample_rate = sf.read(bytesIO_buffer)
    feat, utt_label, utt_shape, tffilename = feat_extract(data, sample_rate, FEAT_TYPE, N_FFT, HOP, VAD, CMVN, EXCLUDE_SHORT)
    likelihood = emnet_validation.o1.eval({x: feat, s: utt_shape}, session=sess4)

    probabilities = softmax(likelihood.ravel().tolist())

    return dict(zip(langList, probabilities))


def do_shuffle(feat, utt_label, utt_shape):
    #### shuffling
    shuffleidx = np.arange(0, len(feat))
    np.random.shuffle(shuffleidx)

    feat = np.array(feat)
    utt_label = np.array(utt_label)
    utt_shape = np.array(utt_shape)

    feat = feat[shuffleidx]
    utt_label = utt_label[shuffleidx]
    utt_shape = utt_shape[shuffleidx]

    feat = feat.tolist()
    utt_label = utt_label.tolist()
    utt_shape = utt_shape.tolist()

    return feat, utt_label, utt_shape


if __name__ == '__main__':
    # c442bfff-9e1c-4af5-b7af-d22c0dd8988b
    raw_file_path = os.path.join(r'/var/spool/asr/nnet3sac', 'c442bfff-9e1c-4af5-b7af-d22c0dd8988b' + '.raw')
    raw_file_path = os.path.join(r'/home/disooqi/projects/log-mel_scale_filter_bank_energy', '2.wav')

    file_format = 'wav'
    if file_format == 'wav':
        y, sr = librosa.core.load(raw_file_path, sr=16000, mono=True, dtype='float')
        feat, utt_label, utt_shape, tffilename = feat_extract(y, sr, FEAT_TYPE, N_FFT, HOP, VAD, CMVN, EXCLUDE_SHORT)
        likelihood = emnet_validation.o1.eval({x: feat, s: utt_shape}, session=sess4)
        probabilities = softmax(likelihood.ravel().tolist())
        print(dict(zip(langList, probabilities)))

    elif file_format == 'raw':
        memory_buffer = BytesIO()
        raw_file_obj = open(raw_file_path, 'rb', os.O_NONBLOCK)
        with contextlib.closing(wave.open(memory_buffer, 'wb')) as wave_obj:
            wave_obj.setnchannels(1)
            wave_obj.setframerate(16000)
            wave_obj.setsampwidth(2)
            raw_file_obj.seek(-640000, 2)
            wave_obj.writeframes(raw_file_obj.read())
        memory_buffer.flush()
        memory_buffer.seek(0)

        acoustic_scores = dialect_estimation(memory_buffer)
        print(acoustic_scores)