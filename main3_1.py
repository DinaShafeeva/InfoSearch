import os
from os.path import join

lemmas = []
path = 'tokens'
for it in os.listdir(path):
    if 'lemmas' in str(it):
        lemmas.append(it)
index = {}
file_and_lemma = {}
for lemma_file in lemmas:
    filenumber = int(lemma_file.split('.')[0].split('_')[0])

    with open(join(path, lemma_file)) as curr_lemma_file:
        text = curr_lemma_file.read().split(sep='\n')
        text.remove('')
        curr_lemmas = list(map(lambda words: words.split()[0], text))
        file_and_lemma.setdefault(filenumber, set()).update(curr_lemmas)
        text = list(map(lambda words: [words.split()[0], []], text))
        index.update(text)

for lemma, lemma_list in index.items():
    for key, value in file_and_lemma.items():
        if lemma in value:
            lemma_list.append(key)
    lemma_list.sort()

with open('inverted_index.txt', 'w') as index_file:
    result = ''
    for lemma, lemma_list in index.items():
        result = f'{result}{lemma} {" ".join([str(x) for x in lemma_list])}\n'
    index_file.write(result)
