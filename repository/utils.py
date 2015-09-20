from django.core.exceptions import ValidationError

import re


def parse_fcs_text(text):
    """return key/value pairs from a delimited string"""
    delimiter = text[0]

    if delimiter != text[-1]:
        raise ValidationError(
            "text in segment does not start and end with delimiter"
        )

    if delimiter == r'|':
        delimiter = '\|'
    elif delimiter == r'\a'[0]:  # test for delimiter being \
        delimiter = '\\\\'  # regex will require it to be \\

    tmp = text[1:-1].replace('$', '')
    # match the delimited character unless it's doubled
    regex = re.compile('(?<=[^%s])%s(?!%s)' % (
        delimiter, delimiter, delimiter))
    tmp = regex.split(tmp)
    return dict(
        zip(
            [x.lower().replace(
                delimiter + delimiter, delimiter) for x in tmp[::2]],
            [x.replace(delimiter + delimiter, delimiter) for x in tmp[1::2]]
        )
    )
