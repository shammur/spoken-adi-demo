#!/home/disooqi/kgs_env/bin/python
__author__ = "disooqi"
__date__ = "25-Feb-2018"
'''
#!/home/disooqi/kgs_env/bin/python
#!/usr/bin/python

script that shows how to postprocess full results from the kaldi-gstreamer-worker, encoded as JSON.
'''
import os
import sys
import json
import logging
from io import BytesIO
import wave
from arabic_dialect_identification.lexical import lexical_identification
from arabic_dialect_identification.acoustic import acoustic_identification



class LastNTokens(object):
    def __init__(self, n):
        # last number of token to be reserved
        self.n = n
        self.tokens = list()

    def get_n_tokens(self):
        return self.tokens[-self.n:]

    def add_tokens_list(self, tokens):
        self.tokens.extend(tokens)
        if len(self.tokens) > self.n:
            self.tokens = self.tokens[-self.n:]


token_list_10 = LastNTokens(10)


def post_process_json(str):
    try:
        # conf = {}
        # if args.conf:
        #     with open(args.conf) as f:
        #         conf = yaml.safe_load(f)
        event = json.loads(str)

        if "result" in event:
            lexical_scores = {u'NOR': 0, u'MSA': 0, u'EGY': 0, u'LAV': 0, u'GLF': 0}
            acoustic_scores = {u'NOR': 0, u'MSA': 0, u'EGY': 0, u'LAV': 0, u'GLF': 0}
            text = event['result']['hypotheses'][0]['transcript']

            tokens = text.strip().split()
            token_list_10.add_tokens_list(tokens)
            utterance = ' '.join(token_list_10.get_n_tokens())
            lexical_scores = lexical_identification.identify_dialect(utterance)

            raw_file = os.path.join(r'/var/spool/asr/nnet3sac', event['id']+'.raw')
            raw_file_size = os.path.getsize(raw_file)

            # if it the audio file has more than 20 SECs which is 1024*600

            if raw_file_size >= 614400:
                buffer = BytesIO()
                wave_file = wave.open(buffer, 'w')
                wave_file.setnchannels(1)
                wave_file.setframerate(16000)
                wave_file.setsampwidth(2)

                file_object = open(raw_file, 'rb', os.O_NONBLOCK)

                file_object.seek(-1024*600, 2)
                wave_file.writeframes(file_object.read())
                wave_file.close()
                buffer.flush()
                buffer.seek(0)

                acoustic_scores = acoustic_identification.dialect_estimation(buffer)
            lexical_weight = 0.3
            acoustic_weight = 0.7
            did_scores = {u'NOR': lexical_scores[u'NOR']*lexical_weight + acoustic_scores[u'NOR']*acoustic_weight,
                          u'MSA': lexical_scores[u'MSA']*lexical_weight + acoustic_scores[u'MSA']*acoustic_weight,
                          u'EGY': lexical_scores[u'EGY']*lexical_weight + acoustic_scores[u'EGY']*acoustic_weight,
                          u'LAV': lexical_scores[u'LAV']*lexical_weight + acoustic_scores[u'LAV']*acoustic_weight,
                          u'GLF': lexical_scores[u'GLF']*lexical_weight + acoustic_scores[u'GLF']*acoustic_weight,
                          }
            # event['result']['hypotheses'].append(lexical_scores)
            # event['result']['hypotheses'].append(acoustic_scores)
            event['result']['hypotheses'].append(did_scores)

        return json.dumps(event)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to process JSON result: %s : %s " % (exc_type, exc_value))
        return str


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")

    lines = []
    while True:
        l = sys.stdin.readline()
        if not l: break # EOF
        if l.strip() == "":
            if len(lines) > 0:
                result_json = post_process_json("".join(lines))
                print result_json
                print
                sys.stdout.flush()
                lines = []
        else:
            lines.append(l)

    if len(lines) > 0:
        result_json = post_process_json("".join(lines))
        print result_json
        lines = []
