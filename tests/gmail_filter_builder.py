"""
For building an managing filters in gmail
"""
import os


gmail_filters = {
    'keeleopi/german': {
        'from': ['feedblitz@transparent.com'],
        'contains': ["German Language Blog"],
    },
    'oluline/finants': {
        'from': ['do-not-reply@coautilitiesemail.com', 'fnbodirect@notify.fnbodirect.com',
                 'customer.service@mail.synchronybank.com', 'noreply@ufcu.org',
                 'postparkmesa@maac.com', 'no-reply@rentcafe.com']
    },
    'reklaamid': {
        'from': [
            'info@mailer.netflix.com',
            'customer.service@candlemart.com',
            '*@lwv.org',
            'reviews@candlemart.com',
            'hrc@hrc.org',
            'sunny@candlemart.com',
            'yourfriends@ties.com',
            '*@redditgifts.com',
            '*@asaustin.org',
            'assistant-noreply@google.com',
            '*.goodreads.com',
            'usmail@expediamail.com',
            'no-reply@vertex.com',
            'noreply-local-guides@google.com',
            'wholefoodsmarket@mail.wholefoodsmarket.com',
            'finnairplus@email.finnair.com',
            'reply@mail.familysearch.org',
            'sales@muehleusa.com',
            'newsletter@email.norwegianreward.com',
            'Honda@emails.honda.com',
            '*@roundrockhonda.com',
            'reply@e.netgear.com',
            'store-news@woot.com',
            'cinamon@key.cinamonkino.com',
            'info@sukamaailm.ee',
            'info@hooandja.ee',
            'IKEA-USA@e.ikea-usa.com',
            'no-reply@pocopay.com'
        ],
        'and_not_from': ['USPSInformedDelivery@usps.gov']
    }
}


def build_filter_str(filter_section_key, filter_section_value):
    """"""
    if filter_section_key in ['from', 'to']:
        filter_str = '{}:({})'.format(filter_section_key, ' OR '.join(filter_section_value))
    elif filter_section_key in ['contains']:
        filter_str = '("{}")'.format('" OR "'.join(filter_section_value))
    elif filter_section_key in ['and_not_from']:
        filter_str = 'AND NOT(from:({}))'.format('" OR "'.join(filter_section_value))
    elif filter_section_key in ['extra']:
        filter_str = 'AND NOT("{}")'.format('" OR "'.join(filter_section_value))

    return filter_str


def get_filter(fname):
    pieces = []
    for k, v in gmail_filters[gmail_filter].items():
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


get_filter('reklaamid')
