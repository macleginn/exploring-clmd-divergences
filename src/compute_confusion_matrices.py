import sqlite3
import json

from queue import Queue
from collections import Counter, defaultdict
from itertools import combinations as combs

import pandas as pd
import numpy as np


def conll2graph(record):
    """
    Converts sentences described using CoNLL-U format 
    (http://universaldependencies.org/format.html) to graphs. 
    Returns a dictionary of nodes (wordforms and POS tags indexed by line numbers)
    together with a graph of the dependencies encoded as adjacency lists of (node_key,
    relation_label, direction[up or down]) tuples.
    """
    graph = {}
    nodes = {}
    for line in record.splitlines():
        if line.startswith('#'):
            continue
        fields = line.strip('\n').split('\t')
        key = fields[0]
        # Ignore compound surface keys for aux, du, etc.
        # Ignore hidden additional nodes for orphan handling
        if '-' in key or '.' in key:
            continue
        wordform = fields[1] 
        pos = fields[3]
        parent = fields[6]
        relation = fields[7]
        nodes[key] = {
            'wordform': wordform,
            'pos': pos,
            'relation': relation,
            'parent': parent
        }
        if key not in graph:
            graph[key] = []
        if parent not in graph:
            graph[parent] = []
        graph[key].append((parent, relation, 'up'))
        graph[parent].append((key, relation, 'down'))
    return (nodes, graph)


def get_path(node1, node2, graph):
    if node1 == node2:
        return []
    
    # BFS with edge labels for paths
    q = Queue()
    # Remembers where we came from and the edge label
    sources = {}
    
    q.put(node1)
    visited = set()
    visited.add(node1)
    
    while not q.empty():
        current = q.get()
        for neighbour, relation, direction in graph[current]:
            if neighbour == node2:
                path = [relation+'_'+direction]
                source = current
                while source != node1:
                    prev_node, prev_relation, prev_direction = sources[source]
                    path.append(prev_relation+'_'+prev_direction)
                    source = prev_node
                return list(reversed(path))
            elif neighbour not in visited:
                sources[neighbour] = (current, relation, direction)
                q.put(neighbour)
            visited.add(neighbour)
            
    raise ValueError("UD graph is not connected.")


strip_direction = lambda x: x.split('_')[0]
strip_subcategory = lambda x: x.split(':')[0]

def get_confusion_matrices(corpus, cursor, collapse_subcategories=False):
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
        
    pos_pairs = []
    path_pairs = []
    
    for i in range(len(en)):
        en_n, en_g    = conll2graph(en[i])
        ko_n, ko_g    = conll2graph(ko[i])
        alignment     = alignments[i]        
        edges         = []
        
             
        # Select edges participating in one-to-one and many-to-one relationships
        # and fill the POS confusion matrix
        for k, v in alignment.items():
            # Add none-to-smth to the POS matrix
            if k == 'X':
                for idx in v:
                    if '.' in idx:
                        continue
                    new_node = ko_n[idx]
                    pos_pairs.append((
                        'None',
                        new_node['pos']
                    ))
                continue
            # Filter out one-to-many
            elif len(v) > 1:
                continue
            head = k
            tail = v[0]
            edges.append((head, tail))
            en_pos = en_n[head]['pos']
            if tail == 'X':
                ko_pos = 'None'
            else:
                ko_pos = ko_n[tail]['pos']
            pos_pairs.append((en_pos, ko_pos))
                    
        
        for pair in combs(edges, 2):
            (en_head, ko_head), (en_tail, ko_tail) = pair
            en_path_arr = get_path(en_head, en_tail, en_g)
            # Don't care for long source-side paths for now
            if len(en_path_arr) > 1:
                continue
            en_path = strip_direction(en_path_arr[0])
            if collapse_subcategories:
                en_path = strip_subcategory(en_path)
            if ko_head == ko_tail:
                ko_path = 'Nodes collapsed'
            # Skip unaligned
            elif ko_head == 'X' or ko_tail == 'X':
                continue
            else:
                ko_path_arr = get_path(ko_head, ko_tail, ko_g)
                ko_path_arr = list(map(strip_direction, ko_path_arr))
                if collapse_subcategories:
                    ko_path = '+'.join(
                        list(map(strip_subcategory, ko_path_arr))
                    )
                else:
                    ko_path = '+'.join(ko_path_arr)
            path_pairs.append((en_path, ko_path))
            
    target_lang_name = corpus.split('-')[1]
        
    pos_dict = defaultdict(list)
    for head_pos, tail_pos in pos_pairs:
        pos_dict['en'].append(head_pos)
        pos_dict[target_lang_name].append(tail_pos)
    pos_df = pd.DataFrame(pos_dict)

    path_dict = defaultdict(list)
    for head_path, tail_path in path_pairs:
        path_dict['en'].append(head_path)
        path_dict[target_lang_name].append(tail_path)
    path_df = pd.DataFrame(path_dict)

    return (
        pd.crosstab(pos_df['en'], pos_df[target_lang_name]), 
        pd.crosstab(path_df['en'], path_df[target_lang_name])
    )


def prettify_confusion_matrix(cm):
    """
    Move columns with the names equal to the names of the rows
    to the fore. Collapse other stuff to "Other".
    """
    rownames = [
        'acl',
        'advcl',
        'advmod',
        'amod',
        'appos',
        'ccomp',
        'compound',
        'conj',
        'fixed',
        'flat',
        'nmod',
        'nsubj',
        'nummod',
        'obj',
        'obl',
        'parataxis',
        'xcomp'
    ]
    idx_dict = {
        k: rownames.index(k) for k in cm.columns if k in rownames
    }
    colnames = sorted(idx_dict, key=lambda x: idx_dict[x])
    if 'Nodes collapsed' in cm.columns:
        colnames.append('Nodes collapsed')
    result = cm.loc[rownames,colnames]
    other_cols = [c for c in cm.columns if c not in colnames]
    tmp = cm.loc[rownames,other_cols]

    # Find the most common other path and its frequency
    mcops = []
    mcop_counts = []
    for i in range(tmp.shape[0]):
        mcop_count = 0
        mcop = ''
        for j in range(tmp.shape[1]):
            if tmp.iloc[i,j] > mcop_count:
                mcop_count = tmp.iloc[i,j]
                mcop = tmp.columns[j]
        mcops.append(mcop)
        mcop_counts.append(mcop_count)

    other_sums = tmp.apply(sum, axis = 1)
    result.insert(result.shape[1], 'Other', other_sums)
    result.insert(result.shape[1], 'MCOP_count', mcop_counts)
    result.insert(result.shape[1], 'MCOP', mcops)
    return result


def get_percentage_cm(cm):
    return round(cm.div(cm.sum(axis=1), axis=0) * 100, 1)


def get_confusion_matries_for_corpus(corpus, cursor, strip_subcategories=False):
    pos_cm, path_cm = get_confusion_matrices(corpus, cursor, strip_subcategories)
    pos_cm_percent  = get_percentage_cm(pos_cm)
    path_cm_percent = get_percentage_cm(path_cm)

    # Select cols also found as rows and collapse the remainder to "Other".
    # This transformation preserves row sums.
    path_cm_small = prettify_confusion_matrix(path_cm)
    # path_cm_small_percent = get_percentage_cm(path_cm_small)

    # Select cols with sum >= 10; this transformation does not preserve row sums
    # Need to take columns from a bigger percentage matrix
    important_cols = [c for c in path_cm.columns if sum(path_cm[c]) >= 10]
    path_cm_reduced = path_cm[important_cols]
    # path_cm_reduced_percent = path_cm_percent[important_cols]
    
    # Spit out files
    pos_cm.to_csv(f'{corpus}_pos_cm.csv')
    pos_cm_percent.to_csv(f'{corpus}_pos_cm_percent.csv')

    if strip_subcategories:
        suffix = "_no_subcats"
    else:
        suffix = ""
        
    path_cm_reduced.to_csv(f'{corpus}_path_cm{suffix}.csv')
    # path_cm_reduced_percent.to_csv(f'{corpus}_path_cm_percent{suffix}.csv')

    path_cm_small.to_csv(f'{corpus}_path_cm_small{suffix}.csv')
    # path_cm_small_percent.to_csv(f'{corpus}_path_cm_small_percent{suffix}.csv')


if __name__ == '__main__':
    conn = sqlite3.connect('../data/pud_current.db')
    cursor = conn.cursor()
    for corpus in [
        'en-fr',
        'en-ru',
        'en-zh',
        'en-ko',
        'en-jp'
    ]:
        get_confusion_matries_for_corpus(corpus, cursor, True)
