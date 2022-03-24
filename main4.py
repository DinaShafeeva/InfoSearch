import os
from os.path import join
from math import log10
from pathlib import Path


def delete_all_by_value(lst: list, value) -> list:
    return [v for v in lst if not v == value]


def get_tokens_files(path) -> list:
    tmp = []
    for it in os.listdir(path):
        if 'tokens' in str(it):
            tmp.append(it)
    return tmp


def get_lemmas_files(path) -> list:
    tmp = []
    for it in os.listdir(path):
        if 'lemmas' in str(it):
            tmp.append(it)
    return tmp


def get_token_tf_idf(token_files, path):
    # { filenumber: (tokens_count, [[token, tkn_count, tf, idf, tf_idf], ... ]), ... }

    # tf
    tmp = {}
    tmp2 = {}
    for token_file in token_files:
        filenumber = int(token_file.split('.')[0].split('_')[0])
        with open(join(path, token_file), 'r') as tkn_file:
            curr_tokens = tkn_file.read().split('\n')
            curr_tokens = delete_all_by_value(curr_tokens, '')
            curr_tokens_count = len(curr_tokens)
            tmp.setdefault(filenumber, (curr_tokens_count, []))
            while curr_tokens:
                curr_token = curr_tokens[0]
                curr_token_count = curr_tokens.count(curr_token)
                tf = curr_token_count / curr_tokens_count
                tmp.get(filenumber)[1].append([curr_token, curr_token_count, tf])
                curr_tokens = delete_all_by_value(curr_tokens, curr_token)
                tmp2.setdefault(curr_token, set()).add(filenumber)

    # idf, tf-idf
    _D = len(token_files)
    for key, value in tmp.items():
        value = value[1]
        for val in value:
            tf = val[2]
            word = val[0]
            idf = log10(_D / len(tmp2.get(word)))
            val.append(idf)
            val.append(tf * idf)
    return tmp


def calculate_tf_for_lemma(filenumber, tkns, token_tf_idf):
    tkn_tf_idf = token_tf_idf.get(filenumber)[1]
    tkn_tf_idf = [v for v in tkn_tf_idf if v[0] in tkns]
    return sum([v[2] for v in tkn_tf_idf])


def get_lemma_tf_idf(lemma_files, path, token_tf_idf):
    tmp = {}
    tmp2 = {}
    for lemma_file in lemma_files:
        filenumber = int(lemma_file.split('.')[0].split('_')[0])
        with open(join(path, lemma_file), 'r') as lmm_file:
            lines = delete_all_by_value(lmm_file.read().split('\n'), '')
            tmp.setdefault(filenumber, [])
            for line in lines:
                words = delete_all_by_value(line.split(' '), '')
                lemma = words[0]
                tkns = words[1:]
                tf = calculate_tf_for_lemma(filenumber, tkns, token_tf_idf)
                tmp.get(filenumber).append([lemma, tkns, tf])
                tmp2.setdefault(lemma, set()).add(filenumber)
    _D = len(lemma_files)
    for key, values in tmp.items():
        for val in values:
            lemma = val[0]
            tf = val[2]
            idf = log10(_D / len(tmp2.get(lemma)))
            val.append(idf)
            val.append(tf * idf)
    return tmp


if __name__ == '__main__':
    path = 'tokens'
    token_files = get_tokens_files(path)
    lemma_files = get_lemmas_files(path)
    token_tf_idf = get_token_tf_idf(token_files, path)
    lemmas_tf_idf = get_lemma_tf_idf(lemma_files, path, token_tf_idf)

    tokens_result_dir = join('.', 'tokens_tf_idf')
    lemmas_result_dir = join('.', 'lemmas_tf_idf')
    Path(tokens_result_dir).mkdir(exist_ok=True)
    Path(lemmas_result_dir).mkdir(exist_ok=True)
    for key, values in token_tf_idf.items():
        values = values[1]
        with open(join(tokens_result_dir, f'tokens_tf_idf_{key}.txt'), 'w') as writable:
            for value in values:
                writable.write(f'{value[0]} {value[2]} {value[4]}\n')
    for key, values in lemmas_tf_idf.items():
        with open(join(lemmas_result_dir, f'lemmas_tf_idf_{key}.txt'), 'w') as writable:
            for value in values:
                writable.write(f'{value[0]} {value[2]} {value[4]}\n')


