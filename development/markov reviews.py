import os
import json
import numpy as np
import re
from kavalkilu import MarkovText


# Read in the reviews
dl_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
rev_fname = 'reviews.json'
rev_fpath = os.path.join(dl_dir, rev_fname)


revs_list = []
for line in open(rev_fpath, 'r'):
    revs_list.append(json.loads(line))

bulk_txt = ''.join([x['reviewText'] for x in revs_list if x['overall'] < 2.0])

mk = MarkovText(bulk_txt)

target_words = ['dataset', 'google sheet', 'high-impact impactivity', 'data']
sentences = mk.generate_n_sentences(3)
for i, sentence in enumerate(sentences):
    sent_split = sentence.split(' ')
    if any([x == 'the' for x in sentence.split(' ')]):
        # find first pos of 'the'
        the_pos = sent_split.index('the')
        # replace next word with bi word
        sent_split[the_pos + 1] = np.random.choice(target_words, 1)[0]
        sentences[i] = ' '.join(sent_split)

print(' '.join(sentences))
