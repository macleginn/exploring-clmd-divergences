import sqlite3
import json

from pprint import pprint
from collections import Counter
from itertools import combinations

from compute_confusion_matrices import conll2graph, get_path


strip_direction   = lambda x: x.split('_')[0]
strip_subcategory = lambda x: x.split(':')[0]


def get_dorr_divergence_counts(corpus, cursor):
    
    result = Counter()

    # Load data
    en = []
    ko = []
    alignments = []
    for en_, ko_, alignment_str in cursor.execute(
        f'SELECT `en`, `ru`, `alignment` FROM `{corpus}` WHERE `verified` = 1'
    ):
        en.append(en_)
        ko.append(ko_)
        alignments.append(json.loads(alignment_str))

    for i in range(len(en)):
        en_n, en_g    = conll2graph(en[i])
        ko_n, ko_g    = conll2graph(ko[i])
        alignment     = alignments[i]

        target_counts = Counter()

        for k, v in alignment.items():
            # Filter out many-to-one
            if k == 'X' or len(v) > 1:
                continue
            target_counts[v[0]] += 1

        for k, v in alignment.items():
            if k == 'X' or target_counts[v[0]] > 1:
                continue
            head = k
            tail = v[0]
            if len(v) == 1 and tail != 'X':
                if (
                    en_n[head]['relation'] == 'nsubj'
                    and
                    ko_n[tail]['relation'] in {'obj', 'obl'}
                ):
                    result['thematic_lax'] += 1
                elif en_n[head]['relation'] == 'obj' and ko_n[tail]['relation'] == 'obl':
                    result['structural'] += 1
                elif en_n[head]['relation'] == 'xcomp' and ko_n[tail]['relation'] == 'advmod':
                    result['demotional'] += 1
            elif len(v) == 2:
                n1 = v[0]
                n2 = v[1]
                if n1 == 'X' or n2 == 'X':
                    continue
                if en_n[head]['relation'] == 'root' and \
                   {ko_n[n1]['relation'], ko_n[n2]['relation']} == {'root', 'obj'}:
                    result['conflational'] += 1

        for h1, h2 in combinations(alignment, 2):
            if h1 == 'X' or h2 == 'X'\
               or len(alignment[h1]) > 1 or len(alignment[h2]) > 1 \
               or alignment[h1][0] == 'X' \
               or alignment[h2][0] == 'X' \
               or target_counts[alignment[h1][0]] > 1 \
               or target_counts[alignment[h2][0]] > 1:
                continue
            t1 = alignment[h1][0]
            t2 = alignment[h2][0]
            path_en = [strip_subcategory(strip_direction(el)) for el in get_path(h1, h2, en_g)]
            path_ko = [strip_subcategory(strip_direction(el)) for el in get_path(t1, t2, ko_g)]
            if en_n[h1]['relation'] == 'root' and ko_n[t1]['relation'] == 'xcomp' \
                    and en_n[h2]['relation'] == 'advmod' and ko_n[t2]['relation'] == 'root':
                    result['promotional'] += 1
            elif path_en == ['nsubj'] and (
                    path_ko == ['nsubj', 'obj']   or
                    path_ko == ['obj',   'nsubj'] or
                    path_ko == ['nsubj', 'iobj']  or
                    path_ko == ['iobj',  'nsubj'] or
                    path_ko == ['nsubj', 'obl']   or
                    path_ko == ['obl',   'nsubj']
                ):
                result['categorial_lax'] += 1
                if (
                    path_ko == ['nsubj', 'obj'] or
                    path_ko == ['obj', 'nsubj']
                ):
                    result['categorial_strict'] += 1
            elif (en_n[h1]['relation'] == 'nsubj' and en_n[h2]['relation'] in {'obj', 'obl'})\
                and (ko_n[t1]['relation'] in {'obj', 'obl'} and ko_n[t2]['relation'] == 'nsubj'):
                result['thematic_full'] += 1
            elif (en_n[h1]['relation'] in {'obj', 'obl'} and en_n[h2]['relation'] == 'nsubj')\
                and (ko_n[t1]['relation'] == 'nsubj' and ko_n[t2]['relation'] in {'obj', 'obl'}):
                result['thematic_full'] += 1

    return result


if __name__ == '__main__':
    conn = sqlite3.connect('pud_current.db')
    cursor = conn.cursor()
    for corpus in [
        'en-fr',
        'en-ru',
        'en-zh',
        'en-ko',
        'en-jp'
    ]:
        result = get_dorr_divergence_counts(corpus, cursor)
        print(corpus +': ')
        for key in [
                'thematic_full',
                'thematic_lax',
                'promotional',
                'demotional',
                'structural',
                'conflational',
                'categorial_strict',
                'categorial_lax'
            ]:
            print(f'{key}: {result[key]}')
        print()
