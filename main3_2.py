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


def calculate(first, second, el):
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


def bool_search():
    stack = []
    while rpn:
        el = rpn.pop(0)
        if el.isalpha():
            stack.append(el)
        else:
            second = stack.pop()
            first = stack.pop()
            stack.append(calculate(first, second, el))
    return stack.pop()


if __name__ == '__main__':
    index = create_index('inverted_index.txt')
    b_s = 'рецепт & салат'
    bool_search_str = add_spaces(b_s)
    rpn = build_rpn(bool_search_str)
    answer = bool_search()
    print(answer)
