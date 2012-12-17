# -*- coding: utf-8 -*-
import logging


def parse_input(tokens, sloppy_validation=False):
    """Parse input tokens.
    
    Take a list of tokens (usually ``sys.argv[1:]``) and parse the "human
    readable" input into a format suitable for machines.

    Args:
        tokens: List of tokens (usually ``sys.argv[1:]``.
        sloppy_validation: Set to True to enable less strict validation. Used
            mainly for testing, default False.

    Returns:
        A 2-tuple containing the data dictionary and the language string. For
        example:

        ({'to': 'bern', 'from': 'zürich'}, 'de')

    Raises:
        ValueError: If "from" or "to" arguments are missing or if both
            departure *and* arrival time are specified.

    """

    if len(tokens) < 2:
        return {}, None

    keyword_dicts = {
        'en': {'from': 'from', 'to': 'to', 'via': 'via',
               'departure': 'departure', 'arrival': 'arrival'},
        'de': {'from': 'von', 'to': 'nach', 'via': 'via',
               'departure': 'ab', 'arrival': 'an'},
        'fr': {'from': 'de', 'to': 'à', 'via': 'via',
               'departure': 'départ', 'arrival': 'arrivée'},
    }

    # Detect language
    intersection_count = lambda a, b: len(set(a).intersection(b))
    intersection_counts = [(lang, intersection_count(keywords.values(), tokens))
                           for lang, keywords in keyword_dicts.items()]
    language = max(intersection_counts, key=lambda x: x[1])[0]
    logging.info('Detected [%s] input' % language)

    # Keywords mapping
    keywords = dict((v, k) for k, v in keyword_dicts[language].iteritems())
    logging.debug('Using keywords: ' + ', '.join(keywords.keys()))

    # Prepare variables
    data = {}
    stack = []

    def process_stack():
        """Process the stack. First item is the key, rest is value."""
        key = keywords.get(stack[0])
        value = ' '.join(stack[1:])
        data[key] = value
        stack[:] = []

    # Process tokens
    for token in tokens:
        if token in keywords.keys():
            if stack:
                process_stack()
        elif not stack:
            continue
        stack.append(token)
    process_stack()

    # Validate data
    if not sloppy_validation:
        if not ('from' in data and 'to' in data):
            raise ValueError('"from" and "to" arguments must be present!')
        if 'departure' in data and 'arrival' in data:
            raise ValueError('You can\'t specify both departure *and* arrival time.')

    logging.debug('Data: ' + repr(data))
    return data, language


    """
    transport.opendata.ch request params:
    - from
    - to
    - via
    - date
    - time
    - isArrivalTime
    - transportations
    - limit
    - page
    - direct
    - sleeper
    - couchette
    - bike
    """
