"""
For building an managing filters in gmail
"""
import os
import json


filter_fp = os.path.join(os.path.expanduser('~'), *['keys', 'email_filters.json'])

with open(filter_fp, 'r') as fp:
    gmail_filters = json.load(fp)


def build_filter_str(filter_section_key, filter_section_value):
    if filter_section_key in ['from', 'to']:
        filter_str = '{}:({})'.format(filter_section_key, ' OR '.join(filter_section_value))
    elif filter_section_key in ['contains']:
        filter_str = '("{}")'.format('" OR "'.join(filter_section_value))
    elif filter_section_key in ['and_not_from']:
        filter_str = 'AND NOT(from:({}))'.format('" OR "'.join(filter_section_value))
    elif filter_section_key in ['extra']:
        filter_str = 'AND NOT("{}")'.format('" OR "'.join(filter_section_value))

    return filter_str


def get_filter(filter_dict, filter_name):
    pieces = []
    for k, v in filter_dict[filter_name].items():
        pieces.append(build_filter_str(k, v))
    result_str = ''
    for piece in pieces:
        if result_str == '':
            result_str += piece
        elif piece[:3] == "AND":
            result_str += " " + piece
        else:
            result_str += ' OR {}'.format(piece)
    return result_str


def write_new_filters(filter_dict, filepath):
    with open(filepath, 'w') as f:
        json.dump(filter_dict, f)


get_filter('reklaamid')
