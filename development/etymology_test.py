import ety


ety.origins('quarantine')[0].pretty
print(ety.tree('quarantine'))


import re


msg = 'cmd -u <@CMDERFA><@LSKJDFEF> -s this'
msg1 = 'cmd --u <@CMDERFA><@LSKJDFEF> -s this'
msg2 = 'process this command -u this that other -p 1 2 3 4 5'
msg3 = 'process this command'
msg4 = 'cmd -u'


def flag_parser(message):
    """Takes in a message string and parses out flags in the string and the values following them
    Args:
        message: str, the command message containing the flags

    Returns:
        dict, flags parsed out into keys

    Example:
        >>> msg = 'process this command -u this that other --p 1 2 3 4 5'
        >>> flag_parser(msg)
        >>> {'cmd': 'process this command', 'u': ['this', 'that', 'other'], 'p': ['1', '2', '3', '4', '5']}
    """
    msg_split = message.split(' ')
    cmd_dict = {'cmd': re.split(r'\-+\w+', message)[0].strip()}
    flag_regex = re.compile(r'^\-+(\w+)')
    for i, part in enumerate(msg_split):
        if flag_regex.match(part) is not None:
            flag = flag_regex.match(part).group(1)
            # Get list of values after the flag up until the next flag
            vals = []
            for val in msg_split[i + 1:]:
                if flag_regex.match(val) is not None:
                    break
                vals.append(val)
            cmd_dict[flag] = vals
    return cmd_dict


