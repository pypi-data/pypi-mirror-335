import re
from w3lib import html


SPECIAL_CHARS = {
    u'\u2009': ' ',
    u'\u202f': ' ',
    u'\u00a0': ' ',
    u'\u2217': '*',
}


def parse_abstract(abstracts):
    """
        - 1 no AbstractText
        - 2 sigle AbstractText
        - 3 multiple abstracts with Labels
        
        * remove tags
        * repalce entities
        * repalce special chars
    """
    if not abstracts:
        abstract = '.'
    elif len(abstracts) == 1:
        abstract = ''.join(abstracts[0].itertext()) or '.'
        abstract = abstract.replace('\n', ' ')
    else:
        real_abstract = None
        for item in abstracts:
            if item.find('sec') is not None:
                real_abstract = item
                break
    
        if real_abstract is not None:
            abstract_list = []
            for part in real_abstract.findall('sec'):
                label = part.findtext('title')
                text = ''.join(part.itertext())
                if label:
                    abstract_list.append('{}: {}'.format(label, text))
                else:
                    abstract_list.append(text)
            abstract = '\n'.join(abstract_list)
        else:
            abstract = '\n'.join(''.join(part.itertext()) for part in abstracts)

    # ===========
    # remove tags
    # ===========
    abstract = html.remove_tags(abstract)

    # ===============
    # repalce entities
    # ===============
    n = 0
    while re.search(r'&.{1,7};', abstract):
        abstract = html.replace_entities(abstract)
        n += 1
        if n > 4:
            print('entities levels > 5')
            print(re.findall(r'&.{1,7};', abstract))
            break

    # =====================
    # replace special chars
    # =====================
    for special, replace in SPECIAL_CHARS.items():
        abstract = abstract.replace(special, replace)

    return abstract
