import os
import re as regexp

import morph as morph
import nltk

nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download("stopwords")
nltk.download('wordnet')
from pymorphy2 import MorphAnalyzer
from nltk import sent_tokenize
from nltk.corpus import stopwords

tokens_file_path = 'tokens/tokens.txt'
lemmas_file_path = 'tokens/lemmas.txt'
tokens_path = 'tokens/'
pages_path = 'output/'
write = 'w'
read = 'r'
morph = MorphAnalyzer()

def clean(file_data):
    pattern = r'<[ ]*style.*?\/[ ]*style[ ]*>'
    file_data = regexp.sub(pattern, ' ', file_data,
                           flags=(regexp.IGNORECASE | regexp.MULTILINE | regexp.DOTALL))
    pattern = r'<[ ]*script.*?\/[ ]*script[ ]*>'
    file_data = regexp.sub(pattern, ' ', file_data,
                           flags=(regexp.IGNORECASE | regexp.MULTILINE | regexp.DOTALL))
    pattern = r'<[ ]*meta.*?>'
    file_data = regexp.sub(pattern, ' ', file_data,
                           flags=(regexp.IGNORECASE | regexp.MULTILINE | regexp.DOTALL))
    pattern = regexp.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    output = regexp.sub(pattern, ' ', file_data)
    return output


def get_words(sentence):
    sentence = sentence.lower()
    sentence = regexp.sub(r"(@[А-Яа-я0-9]+)|([^0-9А-Яа-я \t])|(\w+://\S+)|^rt|http.+?",
                          ' ',
                          sentence)
    sentence = regexp.sub(r"\d+", ' ', sentence)
    sentence = '  '.join([w for w in sentence.split() if w not in stopwords.words("russian")])
    result = sentence.split()
    return result


print('start writing tokens and lemmas')

pages_files = os.listdir(pages_path)

for file in pages_files:
    with open(pages_path + file, read) as input_file:
        tokens = []
        lemmas = {}
        cleaned_text = clean(input_file.read())
        lines = [cleaned_text]
        if cleaned_text.find('\n') != -1:
            lines = cleaned_text.split('\n')
            for line in lines:
                if line:
                    sentences = sent_tokenize(line, language="russian")
                    for sentence in sentences:
                        words = get_words(sentence)
                        for word in words:
                            current_lemma = morph.normal_forms(word)[0]
                            tokens.append(word)
                            print(word)
                            if current_lemma not in lemmas:
                                lemmas[current_lemma] = set()
                            lemmas[current_lemma].add(word)

        with open(tokens_path + file.replace('.html', '_') + 'tokens.txt', write, encoding='utf-8') as output_file:
            for token in tokens:
                output_file.write(token + '\n')
        with open(tokens_path + file.replace('.html', '_') + 'lemmas.txt', write, encoding='utf-8') as output_file:
            for key, values in lemmas.items():
                lemma = key + ' '
                if len(values) <= 1:
                    lemma += key
                else:
                    for value in values:
                        lemma += value + ' '
                output_file.write(lemma + '\n')

print('end writing tokens and lemmas')


