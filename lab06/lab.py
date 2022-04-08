import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

try:
    URL = sys.argv[1]
    FILENAME = sys.argv[2]
    FILENAME = open(URL, 'wb')
except:
    pass

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6

def download_single_file(url_http, chunk_size=8192):
    """
    Downloads a single file with
    """
    toYield = ''
    while toYield != b'':
        toYield = url_http.read(chunk_size)
        yield toYield

def check_status(url_http):
    """
    Checks the status of a url and raises exception or redirects accordingly
    """
    while url_http.status != 200:
        if url_http.status == 404:
            raise HTTPFileNotFoundError
        elif url_http.status == 500:
            raise HTTPRuntimeError
        elif url_http.status == 301 or url_http.status == 302 or url_http.status == 307:
            new_http = url_http.getheader('location')
            url_http = http_response(new_http)
    return url_http


def handle_manifests_parts(url_http):
    """
    Gets all the parts of the manifest
    """
    cache_dic = {}
    toYield = b''
    next_line = ''
    cached = None
    while next_line != b'':
        next_line = url_http.readline()
        #checks if the manifest can be cached
        if next_line[:3].decode('utf-8') == '(*)':
            cached = False
        elif next_line == b'--\n':
            #checks if the part has already been cached
            if toYield[:-1] in cache_dic:
                yield toYield[:-1], True
            #checks if the part can be cached (it hasn't been cached yet)
            elif cached == False:
                cache_dic[toYield[:-1]] = True
                yield toYield[:-1], cached
            #the part cannot be cached
            else:
                yield toYield[:-1], None
            #resets variables to restart checking
            cached = None
            toYield = b''
            continue
        else:
            #adds to the check
            toYield += next_line
    #catches the last part in the manifest
    if toYield[:-1] in cache_dic:
        yield toYield[:-1], True
    else:
        yield toYield[:-1], None

def inside_manifest_part(part, cached, cache_dic = {}):
    """
    Gets all alternative urls from said part
    """
    check, original, part, last, cache = True, part, str(part)[2:-1], 0, None
    #keeps checking until solution is found
    while check:
        #if it has been cached return original value
        if cached == True:
            yield original, True, {}
            break
        #if it has not been cached store it 
        if cached == False and original not in cache_dic:
            cache = b''.join(download_single_file(http_response(original)))
            cache_dic[original] = cache
            yield original, True, {original: cache}
            break
        #if it can't be cached go through urls separating them and checking for 200 status
        checker = ''
        for i in range(last, len(part)):
            if i == len(part)-2:
                check = False
            elif part[i:i+2] == '\\n':
                last = i + 2
                break
            checker += part[i]
        try:
            #iterate until you get 200 status code
            checker = check_status(http_response(checker.encode('utf-8')))
            check = False
            yield checker, False, {}
        except :
            continue

def concat_manifest(url_http, chunk_size=8192, cache_dic={}):
    """
    Concatonates all the parts of a manifest
    """
    for part, cacheable in handle_manifests_parts(url_http):
        for url, cache, dic in inside_manifest_part(part, cacheable):
            #updates dictionary with cached values
            cache_dic.update(dic)
            #if cached return cached value
            if cache == True:
                yield cache_dic[url]
            #if not iterate through function
            else:
                toYield = ''
                while toYield != b'':
                    toYield = url.read(chunk_size)
                    yield toYield


def download_file(url, chunk_size=8192):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    try:
        url_http = check_status(http_response(url))
    except ConnectionError: 
        raise HTTPRuntimeError
    print(url_http)
    # if '-seq' in url:
    #     print('sequence found')
    #     return url_http
    if url_http.getheader('content-type') == 'text/parts-manifest' or url[-6:] == '.parts':
        return concat_manifest(url_http, chunk_size)

    return download_single_file(url_http, chunk_size)


def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    leftover = b''
    is_char_left, is_len_left, flag = False, False, True
    length = 0
    for i in range(4):
        idx = 4
        next_file = next(stream)
        if is_char_left:
            print('char left')
            print(next_file[:leftover])
            idx += leftover
        elif is_len_left:
            print('length left')
            length = int.from_bytes(leftover + next_file[4-len(leftover)])
            flag = False
        while idx < len(next_file):
            if flag:
                length = int.from_bytes(next_file[idx-4:idx], byteorder='big')
                print('for length ', next_file[idx-4:idx])
                print('length ', int.from_bytes(next_file[idx-4:idx], byteorder='big'))
                flag = True
            elif idx + 4 > len(next_file) and next_file[-1] == 0:
                is_len_left, leftover = True, next_file[idx+length:]
            print(next_file[idx:idx+length])
            idx += length + 4
        next_file = next(stream)
        print('getting new file ')



if __name__ == "__main__":
    try:
        URL = sys.argv[1]
        FILENAME = sys.argv[2]
        # FILENAME = open(URL, 'wb')
    except:
        pass
    # print(b''.join(files_from_sequence(download_file('http://mit.edu/6.009/www/lab6_examples/kafka.txt-seq'))))
    # print(b''.join(download_file(
    #     "http://scripts.mit.edu/~6.009/lab6/redir.py/0/cat_poster.jpg.parts"
    # )))
    # print(b''.join(download_file('http://scripts.mit.edu/~6.009/lab6/delayed.py/happycat.png')))
    # print(b''.join(download_file('http://hz.mit.edu/009_lab6/test.parts', 32)))
    # try:
    #     URL = sys.argv[1]
    #     FILENAME = sys.argv[2]
    #     FILENAME = open(URL, 'wb')
    #     download_file(URL)
    # except:
    #     pass
