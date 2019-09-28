"""
Takes in keywords in a txt file and builds it into a strong password
"""

import os
from random import randint
import pandas as pd
import numpy as np


kw_dir = os.path.join(os.path.expanduser('~'), 'Documents')
kw_file = 's6nad.txt'
adj_file = 'omaduss6nad.txt'
spec_chars = list('!#%&?')

# Load the keyword file
with open(os.path.join(kw_dir, kw_file), 'r') as f1, open(os.path.join(kw_dir, adj_file), 'r') as f2:
    keywords_raw = f1.read().split('\n')
    adjs = f2.read().split('\n')

keywords = []
# Go through each keyword, classify it by length and split syllables
for keyword in keywords_raw:
    if len(keyword) < 3:
        continue
    # Mix in adjectives
    for adj in adjs:
        if len(adj) < 3:
            continue
        keyword_split = keyword.split('|')
        rst = randint(0, 8)
        blob = ['{}{}'.format(x, y) for x, y in zip(keyword_split, range(rst, rst + len(keyword_split)))]

        pdict = {
            'a': adj.capitalize(),
            'schar': spec_chars[randint(0, len(spec_chars) - 1)],
            'blob': ''.join(blob)
        }

        keyword_fmt = '{a}{schar}{blob}'.format(**pdict)

        keywords.append({
            'kw': keyword_fmt,
            'kw_len': len(keyword_fmt)
        })

# Feed into dataframe
kw_df = pd.DataFrame(keywords)

# Give detail about keyword distribution for each length
print("Here's a list of keyword combinations:")
print(kw_df.groupby('kw_len').count())

# Get upper and lower limit of keywords
limits = input('Please provide an upper/lower limit (lower,upper)')
limits = limits.split(',')
if len(limits) > 1:
    kw_df = kw_df.query('kw_len >= {} and kw_len <= {}'.format(*limits))
elif len(limits) == 1:
    # Assume upper limit
    kw_df = kw_df.query('kw_len <= {}'.format(*limits))

# Randomly select 5
rands = np.random.choice(kw_df.shape[0], 5, False)
print('Here are your randomly-selected keywords:')
print(kw_df.iloc[rands].to_string(index=False))

