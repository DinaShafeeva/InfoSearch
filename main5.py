import os
import sys
from os.path import join

import PyQt5.QtCore
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer()


def get_lemma(search_query):
    tokens = search_query.split()
    tokens = [tkn.lower() for tkn in tokens if tkn.lower() not in stopwords.words("russian")]
    lemmas = []
    for x in tokens:
        current_lemma = morph.normal_forms(x)[0]
        lemmas.append(current_lemma)
    return lemmas


def get_html_lemmas_tf_idf():
    lemmas_html = dict()
    files = []
    path = 'lemmas_tf_idf/'
    for it in os.listdir(path):
        files.append(it)

    for tf_idf_file in files:
        with open(join(path, tf_idf_file), 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = [line for line in lines if not line == '']
        curr = lemmas_html.setdefault(tf_idf_file.split('.')[0].split('_')[-1], dict())
        for line in lines:
            line_items = line.split(" ")
            lemma = line_items[0]
            lemma_idf = float(line_items[1])
            lemma_tf_idf = float(line_items[2])

            curr.setdefault(lemma, (lemma_idf, lemma_tf_idf))

    return lemmas_html


OR = '|'
AND = '&'
BRACKET_OPEN = '('
BRACKET_CLOSE = ')'


def create_index(index_filename: str) -> dict:
    curr_index = {}
    with open(index_filename, 'r', encoding='utf-8') as index_txt:
        text = index_txt.read().split('\n')
        text.remove('')
        for lemma in text:
            tmp = lemma.split(' ', maxsplit=1)
            curr_index[tmp[0]] = set(tmp[1].split(' '))
    return curr_index


def add_spaces(bool_str: str) -> list:
    tmp = bool_str.replace('|', ' | ') \
        .replace('&', ' & ') \
        .replace('(', ' ( ') \
        .replace(')', ' ) ')
    tmp = tmp.split(' ')
    return [x for x in tmp if not x == '']


def calculate(first, second, el, index):
    operator = set.intersection if el == AND else set.union
    if type(first) == str and type(second) == str:
        first_list = index.setdefault(first, set())
        second_list = index.setdefault(second, set())
        return operator(first_list, second_list)
    elif type(first) == set and type(second) == str:
        second_list = index.setdefault(second, set())
        return operator(first, second_list)
    elif type(first) == str and type(second) == set:
        first_list = index.setdefault(first, set())
        return operator(first_list, second)
    elif type(first) == set and type(second) == set:
        return operator(first, second)
    else:
        raise Exception


def priority(first: str, second: str) -> bool:
    return first == OR and second == AND \
           or first == BRACKET_OPEN and second in [OR, AND]


def build_rpn(bs: list) -> list:
    stack = []
    result = []
    while True:
        try:
            el = bs.pop(0)
        except IndexError:
            while True:
                try:
                    result.append(stack.pop())
                except IndexError:
                    return result
        if el.isalpha():
            result.append(el)
        elif el == BRACKET_OPEN:
            stack.append(el)
        elif el == BRACKET_CLOSE:
            while True:
                _el = stack.pop()
                if _el == BRACKET_OPEN:
                    break
                result.append(_el)
        elif (not stack) or priority(stack[-1], el):
            stack.append(el)
        else:
            while True:
                if stack and (not priority(stack[-1], el)):
                    result.append(stack.pop())
                else:
                    stack.append(el)
                    break


def bool_search(b_s):
    index = create_index('inverted_index.txt')
    bool_search_str = add_spaces(b_s)
    rpn = build_rpn(bool_search_str)
    stack = []
    while rpn:
        el = rpn.pop(0)
        if el.isalpha():
            stack.append(el)
        else:
            second = stack.pop()
            first = stack.pop()
            stack.append(calculate(first, second, el, index))
    result = stack.pop()
    if type(result) == str:
        return index.get(result)
    else:
        return result


def vector_search(query: str) -> list:
    query_lemmas = get_lemma(query)
    td_idf = get_html_lemmas_tf_idf()

    unique_lemmas = set(query_lemmas)
    founded_files = bool_search(" | ".join(query_lemmas))
    lemmas_idf: dict = dict()
    for file in founded_files:
        unique_lemmas.update(set(td_idf.get(file).keys()))

    files_vector = []
    for file in founded_files:
        html_lemma_info: dict = td_idf.get(file)
        html_lemmas: set = set(html_lemma_info.keys())
        vector = []
        for lemma in unique_lemmas:
            if lemma in html_lemmas:
                lemma_idf, lemma_tf_idf = html_lemma_info.get(lemma)
                vector.append(lemma_tf_idf)
                lemmas_idf.setdefault(lemma, lemma_idf)
            else:
                vector.append(0.0)
        files_vector.append([file, vector])

    query_vector = []
    for lemma in unique_lemmas:
        if lemma in query_lemmas:
            lemma_idf = lemmas_idf.get(lemma)
            lemma_tf = query_lemmas.count(lemma) / len(query_lemmas)
            lemma_tf_idf = lemma_tf * lemma_idf
            query_vector.append(lemma_tf_idf)
        else:
            query_vector.append(0.0)

    for file_vector in files_vector:
        file_vector.append(cosine_similarity(file_vector[1], query_vector))

    files_vector = sorted(files_vector, key=lambda d: d[2], reverse=True)

    return [[d[0], d[2]] for d in files_vector]


def cosine_similarity(a: list, b: list):
    numerator = 0
    a_den = 0
    b_den = 0
    if not len(a) == len(b):
        raise Exception
    for i in range(0, len(a)):
        numerator += a[i] * b[i]
        a_den += a[i] * a[i]
        b_den += b[i] * b[i]
    return numerator / (a_den * b_den)


def make_links(vectors):
    path = "output/index.txt"
    links = []
    with open(path, 'r', encoding='utf-8') as index_txt:
        text = index_txt.read().split('\n')

    for vector in vectors:
        curr_vector = vector[0]
        for line in text:
            curr_line = line.split(' - ')
            if curr_line[0] == curr_vector:
                links.append(curr_line[1])

    return links


class Searcher(PyQt5.QtCore.QObject):
    def __init__(self):
        PyQt5.QtCore.QObject.__init__(self)

    @PyQt5.QtCore.pyqtSlot(str)
    def search(self, arg1):
        engine.rootContext().setContextProperty('linksModel', [])

        for link in make_links(vector_search(arg1)):
            links.addLink(LinkListItem("<a href='" + link + "'>" + link + '</a>'))
            print(link)

        engine.rootContext().setContextProperty('linksModel', links)


class LinkListItem(PyQt5.QtCore.QObject):
    def __init__(self, link: str, parent=None):
        super().__init__(parent)
        self.link = link

    @PyQt5.QtCore.pyqtProperty('QString')
    def path(self):
        return self.link


class LinkList(PyQt5.QtCore.QAbstractListModel):
    def __init__(self, links: list, parent=None):
        super().__init__(parent)
        self.links = links

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.links)

    def data(self, index: PyQt5.QtCore.QModelIndex, role=None):
        if role == PyQt5.QtCore.Qt.DisplayRole:
            return self.links[index.row()]

    def addLink(self, link):
        self.beginInsertRows(PyQt5.QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self.links.append(link)
        self.endInsertRows()


links = LinkList([])
if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    searcher = Searcher()
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    engine.rootContext().setContextProperty("searcher", searcher)
    engine.load('hm5/ui/main.qml')

    sys.exit(app.exec())
