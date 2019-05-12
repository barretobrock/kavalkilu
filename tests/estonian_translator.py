#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Takes in an Estonian word, finds English equivalent,
    as well as different Estonian declinations and example sentences
"""

import re
import urllib.request as req
from lxml import etree
from collections import OrderedDict


word_list = [
    'päikeseprillid',
    'restoran'
]

word = 'restoran'


def get_root(word):
    """Retrieves the root word (nom. sing.) from Lemmatiseerija"""
    # First, look up the word's root with the lemmatiseerija
    lemma_url = 'http://www.filosoft.ee/lemma_et/lemma.cgi?word={}'
    content = req.urlopen(lemma_url.format(word)).read()
    content = str(content)
    # Use static placeholder un front of word to slice section of lemma
    front_placeholder = '<strong>S&otilde;na lemma on:</strong><br>'
    rear_placeholder = '<br>\\n'
    try:
        front_placeholder_idx = content.index(front_placeholder)
        rear_placeholder_idx = content.index(rear_placeholder)
    except ValueError:
        print('The word "{}" was not found in Lemma. This might need to be done manually'.format(word))
        return None

    root_word = content[front_placeholder_idx + len(front_placeholder):rear_placeholder_idx]
    return root_word


def prep_for_xpath(url):
    """Takes in a url and returns a tree that can be searched using xpath"""
    content = req.urlopen(url)
    parser = etree.HTMLParser()
    tree = etree.parse(content, parser)
    return tree


# Using the root, look up the English version
root_word = get_root(word)


def get_declinations(word):
    """Retrieves declinations in Nom, Gen, Part in singular and plural for given word"""
    ekisynt_base_url = 'http://www.filosoft.ee/gene_et/gene.cgi?word={}&{}'
    params = 'gi=sg+n%2C&gi=pl+n%2C&gi=sg+g%2C&gi=pl+g%2C&gi=sg+p%2C&gi=pl+p%2C'
    content = req.urlopen(ekisynt_base_url.format(word, params)).read()
    content = str(content)
    front_placeholder = 'Eesti keele s&uuml;ntesaator</h2>\\n<table border="0" cellspacing="0" cellpadding="10"><tr><td class="MoreGray">'
    rear_placeholder = '</tr>\\n</table><hr>\\n<p class="Copyright">'
    try:
        front_placeholder_idx = content.index(front_placeholder)
        rear_placeholder_idx = content.index(rear_placeholder)
    except ValueError:
        print('The word "{}" was not found in Süntesaator. This might need to be done manually'.format(word))
        return None
    # Remove all the header/javascript stuff from the response & clean it up
    trimmed_content = content[front_placeholder_idx + len(front_placeholder):rear_placeholder_idx]
    trimmed_content = trimmed_content.replace('&nbsp;', '')
    # Begin extracting the different cases
    cases = OrderedDict((
        ('sng-nom', 'sgn'),
        ('sng-gen', 'sgg'),
        ('sng-prt', 'sgp'),
        ('plu-nom', 'pln'),
        ('plu-gen', 'plg'),
        ('plu-prt', 'plp'),
    ))

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


def get_translation(word):
    """Returns the English translation of the Estonian word"""
    # Find the English translation of the word using EKI
    eki_url = 'http://www.eki.ee/dict/ies/index.cgi?Q={}&F=V&C06=en'
    content = prep_for_xpath(eki_url.format(word))

    results = content.xpath('//div[@class="tervikart"]')
    result = []
    for i in range(0, len(results)):
        et_result = content.xpath('(//div[@class="tervikart"])[{}]/*/span[@lang="et"]'.format(i + 1))
        en_result = content.xpath('(//div[@class="tervikart"])[{}]/*/span[@lang="en"]'.format(i + 1))
        # Process text in elements
        et_result = [''.join(x.itertext()) for x in et_result]
        en_result = [''.join(x.itertext()) for x in en_result]
        if word in et_result:
            result += en_result

    if len(result) > 0:
        # Make all entries lowercase and remove dupes
        result = list(set(map(str.lower, result)))
        return ', '.join(result)
    else:
        return None

# Find example sentence using the seletav sõnaraamat
def get_examples(word):
    """Returns some example sentences of the Estonian word"""
    # Find the English translation of the word using EKI
    ekss_url = 'http://www.eki.ee/dict/ekss/index.cgi?Q={}&F=M'
    content = prep_for_xpath(ekss_url.format(word))

    results = content.xpath('//div[@class="tervikart"]')
    exp_list = []
    for i in range(0, len(results)):
        result = content.xpath('(//div[@class="tervikart"])[{}]/*/span[@class="m leitud_id"]'.format(i + 1))
        examples = content.xpath('(//div[@class="tervikart"])[{}]/*/span[@class="n"]'.format(i + 1))
        # Process text in elements
        result = [''.join(x.itertext()) for x in result]
        examples = [''.join(x.itertext()) for x in examples]
        if word in result:
            re.split('[?\.!]', ''.join(examples))
            exp_list += re.split('[?\.!]', ''.join(examples))
            # Strip of leading / tailing whitespace
            exp_list = [x.strip() for x in exp_list]
            return exp_list

    return None




