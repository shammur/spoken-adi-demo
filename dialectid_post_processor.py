#!/usr/bin/python
'''
Sample script that shows how to postprocess full results from the kaldi-gstreamer-worker, encoded as JSON.

It adds a sentence confidence score to the 1-best hypothesis, deletes all other hypotheses and
adds a dot (.) to the end of the 1-best hypothesis. It assumes that the results contain at least two hypotheses,
The confidence scores are now normalized
'''

import sys
import json
import logging
from arabic_dialect_identification.lexical import lexical_identification



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
            text = event['result']['hypotheses'][0]['transcript']

            tokens = text.strip().split()
            token_list_10.add_tokens_list(tokens)
            utterance = ' '.join(token_list_10.get_n_tokens())
            did_scores = lexical_identification.identify_dialect(utterance)
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
