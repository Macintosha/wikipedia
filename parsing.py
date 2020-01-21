import re

import requests
from bs4 import BeautifulSoup

V = {}
set_first_url = set()
set_second_url = set()
dict_path_queue1 = list()
dict_path_queue2 = list()
path_url1_to_utl2 = list()
path_url2_to_utl1 = list()
first_path_url1 = set()
second_path_url1 = set()
first_path_url2 = set()
second_path_url2 = set()


def get_refs(ref: str):
    r = requests.get(f'https://en.wikipedia.org/wiki/{ref}')
    if r.status_code != 200:
        return 'Error'
    soup = BeautifulSoup(r.text, features='html.parser')
    cont = soup.findAll('div', attrs={'class': 'mw-parser-output'})
    refs = list()
    for div in cont:
        refs += re.findall(r'href="/wiki/([^:]*?)"', str(div))
    return set(refs)


def random_page():
    url = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    if url.status_code != 200:
        return str()
    return url.url.split('/').pop()


def clear_versh():
    return {'in': set(), 'out': set()}


def add_url_to_set_out(url_name: str, set_save: set):
    new_set_url = {url_name}

    flag = True
    while flag:
        flag = False
        transit_set = new_set_url
        new_set_url = set()
        for name in transit_set:
            if name not in set_save:
                if V.get(name) is not None:
                    new_set_url.update(V.get(name)['out'])
                    flag = True
                set_save.add(name)


def add_url_to_set_in(url_name: str, set_save: set):

    new_set_url = {url_name}

    flag = True
    while flag:
        flag = False
        transit_set = new_set_url
        new_set_url = set()
        for name in transit_set:
            if name not in set_save:
                if V.get(name) is not None:
                    new_set_url.update(V.get(name)['in'])
                    flag = True
                set_save.add(name)


def create_set(date: list):
    first_set, second_set, first_queue, second_queue, first_path1, second_path1, *_ = date
    first_path2, second_path2, url1, url2 = _

    name = str()
    while len(first_queue) > 0 and len(name) == 0:
        name = first_queue.pop(0)
        if name not in first_set:
            name = str()

    if len(name) == 0:
        return 0

    if V.get(name) is None:
        V[name] = clear_versh()

    out_names = get_refs(name)
    V.get(name)['out'] = out_names
    first_flag = False
    second_flag = False
    for names in out_names:
        if V.get(names) is None:
            V[names] = clear_versh()
            first_set.add(names)
            first_queue.append(names)
        V.get(names)['in'].add(name)

        if names == url1 or names in second_path1:
            first_flag = True

        if names == url2 or names in second_path2:
            second_flag = True

    for names in out_names:
        add_url_to_set_out(names, first_path1)
    first_set.discard(name)
    if name in first_path2:
        for names in out_names:
            add_url_to_set_out(names, first_path2)
    second_set.discard(name)

    if first_flag:
        add_url_to_set_in(name, second_path1)
    if second_flag:
        add_url_to_set_in(name, second_path2)


def search_path(set_urls: set, url1: str, url2: str):
    lengths = dict()
    set_urls.add(url1)
    set_urls.add(url2)
    lengths[-1] = set(set_urls)
    lengths[0] = {url1}
    lengths[-1].discard(url1)
    i = 1
    flag = True
    while len(lengths[-1]) and flag and i < 70:
        lengths[i] = set()
        for value in lengths[i - 1]:
            for url in V[value]['out']:
                if url in lengths[-1]:
                    lengths[i].add(url)
                    lengths[-1].discard(url)
                    if url == url2:
                        flag = False
        i += 1

    path = [url2]
    for j in range(2, i):
        path.insert(0, (V[path[0]]['in'] & lengths[i - j]).pop())
    path.insert(0, url1)
    return path


if __name__ == '__main__':

    first_url = random_page()
    second_url = random_page()
    print('From: ' + str(first_url))
    print('To: ' + str(second_url))

    if len(set_first_url) == 0:
        dict_path_queue1 = [first_url]
        set_first_url = set(dict_path_queue1)
    if len(set_second_url) == 0:
        dict_path_queue2 = [second_url]
        set_second_url = set(dict_path_queue2)

    f = open('text.txt', 'w')
    first_date = [
        set_first_url,
        set_second_url,
        dict_path_queue1,
        dict_path_queue2,
        first_path_url1,
        second_path_url1,
        first_path_url2,
        second_path_url2,
        first_url,
        second_url,
    ]

    second_date = [
        set_second_url,
        set_first_url,
        dict_path_queue2,
        dict_path_queue1,
        first_path_url2,
        second_path_url2,
        first_path_url1,
        second_path_url1,
        second_url,
        first_url
    ]
    for i in range(500):

        create_set(first_date)
        create_set(second_date)

        if len(path_url1_to_utl2) == 0 and len(first_path_url1 & second_path_url2):
            path_url1_to_utl2 = search_path(first_path_url1 & second_path_url2, first_url, second_url)

        if len(path_url2_to_utl1) == 0 and len(first_path_url2 & second_path_url1):
            path_url2_to_utl1 = search_path(first_path_url2 & second_path_url1, second_url, first_url)

        if len(path_url1_to_utl2) > 0 and len(path_url2_to_utl1) > 0:
            break

    if len(path_url1_to_utl2) > 0 and len(path_url2_to_utl1) > 0:
        f.write(f'{first_url}->{second_url} len: {len(path_url1_to_utl2) - 1} path: {path_url1_to_utl2} \n')
        f.write(f'{second_url}->{first_url} len: {len(path_url2_to_utl1) - 1} path: {path_url2_to_utl1}')
    elif len(path_url1_to_utl2) > 0:
        f.write(f'{first_url}->{second_url} len: {len(path_url1_to_utl2) - 1} path: {path_url1_to_utl2} \n')
        f.write(f'There is no way from {second_url} to {first_url}')
    elif len(path_url2_to_utl1) > 0:
        f.write(f'There is no way from {first_url} to {second_url} \n')
        f.write(f'{second_url}->{first_url} len: {len(path_url2_to_utl1) - 1} path: {path_url2_to_utl1}')

    print(f'{first_url}->{second_url} len: {len(path_url1_to_utl2) - 1} path: {path_url1_to_utl2}')
    print(f'{second_url}->{first_url} len: {len(path_url2_to_utl1) - 1} path: {path_url2_to_utl1}')
    f.close()
