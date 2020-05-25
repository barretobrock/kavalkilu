#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Takes in an Estonian word, finds English equivalent,
    as well as different Estonian declinations and example sentences
"""

import re
import urllib.parse as parse
import requests
from io import StringIO
from lxml import etree
import ety


word_list = [
    'päikeseprillid',
    'restoran'
]

word = 'restoran'


def get_root(word):
    """Retrieves the root word (nom. sing.) from Lemmatiseerija"""
    # First, look up the word's root with the lemmatiseerija
    lemma_url = f'https://www.filosoft.ee/lemma_et/lemma.cgi?word={parse.quote(word)}'
    content = requests.get(lemma_url).content
    content = str(content, 'utf-8')
    # Use static placeholder un front of word to slice section of lemma
    front_placeholder = '<strong>S&otilde;na lemma on:</strong><br>'
    rear_placeholder = '<br>\n'
    try:
        front_placeholder_idx = content.index(front_placeholder)
        rear_placeholder_idx = content.index(rear_placeholder)
    except ValueError:
        return None

    return content[front_placeholder_idx + len(front_placeholder):rear_placeholder_idx]


def prep_for_xpath(url):
    """Takes in a url and returns a tree that can be searched using xpath"""
    page = requests.get(url)
    html = page.content.decode('utf-8')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser=parser)
    return tree

word = 'quarantine'
url = f'https://www.etymonline.com/search?q={parse.quote(word)}'
content = prep_for_xpath(url)
results = content.xpath('//div[contains(@class, "word--C9UPa")]')
output = ''
if len(results) > 0:
    for result in results:
        name = ' '.join([x for l in result.xpath('object/a') for x in l.itertext()])
        if word in name:
            desc = ' '.join([x for l in result.xpath('object/section') for x in l.itertext()])
            desc = ' '.join([f'_{x}_' for x in desc.split('\n') if x.strip() != ''])
            output += f'*{name}*:\n_{desc}_\n'

etytree = ety.tree('quarantine')
if etytree is not None:
    output = f'\n{etytree.__str__()}\n {output}'

# Using the root, look up the English version
root_word = get_root(word)

item_str = ''
for l in result.xpath('object/a'):
    for x in l.iter():
        for item in [x.text, x.tail]:
            if item is not None:
                if item.strip() != '':
                    item_str += f' {item}'


def get_declinations(input_word, word_type='noun'):
    """Retrieves declinations in Nom, Gen, Part in singular and plural for given word"""
    ekisynt_base_url = 'http://www.filosoft.ee/gene_et/gene.cgi?word={}&{}'

    verb_types = {'a': 'past'}

    verb_codes = ['ti', 'sin', 'sid', 's', 'sime', 'site', 'sid']
    verb_units = ['passive', '1st p sing', '2nd p sing', '3rd p sing', '1st p plu', '2nd p plu', '3rd p plur']
    verb_ex = ['it was <verb>ed', 'I <verb>ed', 'you (sng/informal) <verb>ed', 's/he it <verb>ed', 'we <verb>ed', 'you (pl/formal) <verb>ed', 'they <verb>ed']
    verbs = 'p=1;p=2;p=3;p=4;p=5;p=6;p=0'

    [{'code': f'{verb_codes[i]}', 'class': 'verb', 'subclass': 'past', 'desc': x, 'ex': verb_ex[i]} for i, x in enumerate(verb_units)]

    case_dict = [
        {'code': 'sg+n', 'class': 'noun', 'subclass': 'singular', 'case': 'NOMINATIVE'},
        {'code': 'sg+g', 'class': 'noun', 'subclass': 'singular', 'case': 'GENITIVE'},
        {'code': 'sg+p', 'class': 'noun', 'subclass': 'singular', 'case': 'PARTITIVE'},
        {'code': 'sg+ill,+adt', 'class': 'noun', 'subclass': 'singular', 'case': 'ILLATIVE'},
        {'code': 'sg+in,+mas', 'class': 'noun', 'subclass': 'singular', 'case': 'INESSIVE'},
        {'code': 'sg+el,+mast', 'class': 'noun', 'subclass': 'singular', 'case': 'ELATIVE'},
        {'code': 'sg+all', 'class': 'noun', 'subclass': 'singular', 'case': 'ALLATIVE'},
        {'code': 'sg+ad', 'class': 'noun', 'subclass': 'singular', 'case': 'ADESSIVE'},
        {'code': 'sg+abl', 'class': 'noun', 'subclass': 'singular', 'case': 'ABLATIVE'},
        {'code': 'sg+tr,+maks', 'class': 'noun', 'subclass': 'singular', 'case': 'TRANSLATIVE'},
        {'code': 'sg+ter', 'class': 'noun', 'subclass': 'singular', 'case': 'TERMINATIVE'},
        {'code': 'sg+es', 'class': 'noun', 'subclass': 'singular', 'case': 'ESSIVE'},
        {'code': 'sg+ab,+mata', 'class': 'noun', 'subclass': 'singular', 'case': 'ABESSIVE'},
        {'code': 'sg+kom', 'class': 'noun', 'subclass': 'singular', 'case': 'COMITATIVE'},
        {'code': 'pl+n', 'class': 'noun', 'subclass': 'plural', 'case': 'NOMINATIVE'},
        {'code': 'pl+g', 'class': 'noun', 'subclass': 'plural', 'case': 'GENITIVE'},
        {'code': 'pl+p', 'class': 'noun', 'subclass': 'plural', 'case': 'PARTITIVE'},
        {'code': 'pl+ill', 'class': 'noun', 'subclass': 'plural', 'case': 'ILLATIVE'},
        {'code': 'pl+in', 'class': 'noun', 'subclass': 'plural', 'case': 'INESSIVE'},
        {'code': 'pl+el', 'class': 'noun', 'subclass': 'plural', 'case': 'ELATIVE'},
        {'code': 'pl+all', 'class': 'noun', 'subclass': 'plural', 'case': 'ALLATIVE'},
        {'code': 'pl+ad', 'class': 'noun', 'subclass': 'plural', 'case': 'ADESSIVE'},
        {'code': 'pl+abl', 'class': 'noun', 'subclass': 'plural', 'case': 'ABLATIVE'},
        {'code': 'pl+tr', 'class': 'noun', 'subclass': 'plural', 'case': 'TRANSLATIVE'},
        {'code': 'pl+ter', 'class': 'noun', 'subclass': 'plural', 'case': 'TERMINATIVE'},
        {'code': 'pl+es', 'class': 'noun', 'subclass': 'plural', 'case': 'ESSIVE'},
        {'code': 'pl+ab', 'class': 'noun', 'subclass': 'plural', 'case': 'ABESSIVE'},
        {'code': 'pl+kom', 'class': 'noun', 'subclass': 'plural', 'case': 'COMITATIVE'},
        {'code': 'takse', 'class': 'verb', 'subclass': 'present', 'desc': '{subclass} passive', 'ex': 'it is <verb>ed'},
        {'code': 'n', 'class': 'verb', 'subclass': 'present', 'desc': '1st p {subclass} sing', 'ex': 'I <verb>'},
        {'code': 'd', 'class': 'verb', 'subclass': 'present', 'desc': '2nd p {subclass} sing', 'ex': 'you (sng/informal) <verb>'},
        {'code': 'b', 'class': 'verb', 'subclass': 'present', 'desc': '3rd p {subclass} sing', 'ex': 's/he it <verb>'},
        {'code': 'me', 'class': 'verb', 'subclass': 'present', 'desc': '1st p {subclass} plu', 'ex': 'we <verb>'},
        {'code': 'te', 'class': 'verb', 'subclass': 'present', 'desc': '2nd p {subclass} plu', 'ex': 'you (pl/formal) <verb>'},
        {'code': 'vad', 'class': 'verb', 'subclass': 'present', 'desc': '3rd p {subclass} plur', 'ex': 'they <verb>'},
        {'code': 'ti', 'class': 'verb', 'subclass': 'past', 'desc': '{subclass} passive', 'ex': 'it was <verb>ed'},
        {'code': 'sin', 'class': 'verb', 'subclass': 'past', 'desc': '1st p {subclass} sing', 'ex': 'I <verb>ed'},
        {'code': 'sid', 'class': 'verb', 'subclass': 'past', 'desc': '2nd p {subclass} sing', 'ex': 'you (sng/informal) <verb>ed'},
        {'code': 's', 'class': 'verb', 'subclass': 'past', 'desc': '3rd p {subclass} sing', 'ex': 's/he it <verb>ed'},
        {'code': 'sime', 'class': 'verb', 'subclass': 'past', 'desc': '1st p {subclass} plu', 'ex': 'we <verb>ed'},
        {'code': 'site', 'class': 'verb', 'subclass': 'past', 'desc': '2nd p {subclass} plu', 'ex': 'you (pl/formal) <verb>ed'},
        {'code': 'sid', 'class': 'verb', 'subclass': 'past', 'desc': '3rd p {subclass} plu', 'ex': 'they <verb>ed'},
        {'code': 'gu', 'class': 'verb', 'subclass': 'imperative', 'desc': '3rd p {subclass} sing', 'ex': 'let s/he/it <verb>'},
        {'code': 'gem', 'class': 'verb', 'subclass': 'imperative', 'desc': '2nd p {subclass} plu', 'ex': 'let\'s <verb>'},
        {'code': 'o', 'class': 'verb', 'subclass': 'present', 'desc': '{subclass} negative', 'ex': 'does not <verb>'},
        {'code': 'ge', 'class': 'verb', 'subclass': 'present', 'desc': '{subclass} imperative plu/formal', 'ex': '<verb>!'},
        {'code': 'ge', 'class': 'verb', 'subclass': 'present', 'desc': '{subclass} imperative plu/formal', 'ex': '<verb>!'},
    ]
    # Try to build the params
    if word_type == 'noun':
        params = '&'.join([f'gi={x["code"]},' for x in case_dict if x['class'] == 'noun'])
    elif word_type == 'verb':
        params = 'p=1&p=4&p=2&p=5&p=3&p=6&p=0&a=0&a=1&kv=0&kv=1&kv=2&kv=3&gif=da%2C&gif=des%2C&gif=nud%2C&gif=tud%2C&gif=v%2C&guess=on'
        # params = '&'.join([f'{x["code"]}' for x in case_dict if x['class'] == 'verb'])

    content = req.urlopen(ekisynt_base_url.format(word, params.replace(',', '%2C'))).read()
    content = str(content)
    front_placeholder = 'Eesti keele s&uuml;ntesaator</h2>\\n<table border="0" cellspacing="0" cellpadding="10"><tr><td class="MoreGray">'
    rear_placeholder = '</tr>\\n</table><hr>\\n<p class="Copyright">'
    try:
        front_placeholder_idx = content.index(front_placeholder)
        rear_placeholder_idx = content.index(rear_placeholder)
    except ValueError:
        print(f'Ei leidnud sõna „{input_word}“ Süntesaatori veebileheküljel. '
              f'Käsitsi otsides võib paremad tulemused juhtuda.')
        return None
    # Remove all the header/javascript stuff from the response & clean it up
    trimmed_content = content[front_placeholder_idx + len(front_placeholder):rear_placeholder_idx]
    trimmed_content = trimmed_content.replace('&nbsp;', '')
    # Begin extracting the different cases

    # This is where we'll store our final result
    declinations = {
        'sng': [],
        'plu': []
    }
    for k, v in cases.items():
        # Go through each group, retrieve the case of each word
        print('working on {}'.format(v))
        prefix = '{},//<br>'.format(v)
        suffix = '</td>'
        # Find the location of the case and strip to the beginning
        case = trimmed_content[trimmed_content.index(prefix) + len(prefix):]
        # Strip text after
        try:
            case = case[:case.index(suffix)]
        except ValueError:
            print('No declination found for {}'.format(k))

        # If multiple words are given, they will be separated by <br>
        case = case.replace('<br>', ', ')
        # Feed into the dict
        if 'sng' in k:
            declinations['sng'].append(case)
        else:
            declinations['plu'].append(case)

    return declinations


def get_translation(word, target='en'):
    """Returns the English translation of the Estonian word"""
    # Find the English translation of the word using EKI
    eki_url = f'http://www.eki.ee/dict/ies/index.cgi?Q={parse.quote(word)}&F=V&C06={target}'
    content = prep_for_xpath(eki_url)

    results = content.xpath('//div[@class="tervikart"]')
    result = []
    for i in range(0, len(results)):
        et_result = content.xpath('(//div[@class="tervikart"])[{}]/*/span[@lang="et"]'.format(i + 1))
        en_result = content.xpath('(//div[@class="tervikart"])[{}]/*/span[@lang="en"]'.format(i + 1))
        # Process text in elements
        et_result = [''.join(x.itertext()) for x in et_result]
        en_result = [''.join(x.itertext()) for x in en_result]
        if target == 'en':
            if word in et_result:
                result += en_result
        else:
            if word in en_result:
                result += et_result

    if len(result) > 0:
        # Make all entries lowercase and remove dupes
        result = list(set(map(str.lower, result)))
        return ', '.join(result)
    else:
        return None

# Find example sentence using the seletav sõnaraamat
def get_examples(word, max_n=5):
    """Returns some example sentences of the Estonian word"""
    # Find the English translation of the word using EKI
    ekss_url = f'http://www.eki.ee/dict/ekss/index.cgi?Q={parse.quote(word)}&F=M'
    content = prep_for_xpath(ekss_url)

    results = content.xpath('//div[@class="tervikart"]')
    exp_list = []
    for i in range(0, len(results)):
        result = content.xpath(f'(//div[@class="tervikart"])[{i + 1}]/*/span[@class="m leitud_id"]')
        examples = content.xpath(f'(//div[@class="tervikart"])[{i + 1}]/*/span[@class="n"]')
        # Process text in elements
        result = [''.join(x.itertext()) for x in result]
        examples = [''.join(x.itertext()) for x in examples]
        if word in result:
            re.split('[?\.!]', ''.join(examples))
            exp_list += re.split('[?\.!]', ''.join(examples))
            # Strip of leading / tailing whitespace
            exp_list = [x.strip() for x in exp_list]
            if len(exp_list) > max_n:
                exp_list = [exp_list[x] for x in np.random.choice(len(exp_list), max_n, False).tolist()]
            return '\n'.join([f'`{x}`' for x in exp_list])

    return f'No example sentences found for `{word}`'




