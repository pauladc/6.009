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
    toYield = ''
    while toYield != b'':
        toYield = url_http.read(chunk_size)
        yield toYield

def check_status(url_http):
    while url_http.status != 200:
        if url_http.status == 404:
            raise HTTPFileNotFoundError
        elif url_http.status == 500:
            raise HTTPRuntimeError
        elif url_http.status == 301 or url_http.status == 302 or url_http.status == 307:
            new_http = url_http.getheader('location')
            url_http = http_response(new_http)
    return url_http

def handle_manifests(url_http):
    toYield = b''
    next_line = ''
    while next_line != b'':
        next_line = url_http.readline()
        print(next_line)
        if next_line == b'--\n':
            print(toYield[:-1])
            yield toYield[:-1]
            toYield = b''
            continue
        toYield += next_line
    yield toYield

def inside_manifest(manifest):
    check = True
    manifest = str(manifest)[2:-1]
    last = 0
    no_new_line = True
    while check:
        checker = ''
        for i in range(last, len(manifest)):
            if i == len(manifest)-2:
                check = False
            elif manifest[i:i+2] == '\\n':
                last, no_new_line = i + 2, False
                break
            checker += manifest[i]
        if no_new_line:
            if manifest[-2:] == '\\n':
                checker = manifest[:-2]
        try:
            checker = check_status(http_response(checker.encode('utf-8')))
            check = False
        except :
            continue
    yield checker

def concat_manifest(url_http, chunk_size=8192):
    for part in handle_manifests(url_http):
        for url in inside_manifest(part):
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
    if url_http.getheader('content-type') == 'text/parts-manifest' or url[-6:] == '.parts':
        return concat_manifest(url_http, chunk_size)



    return download_single_file(url_http, chunk_size)


def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    raise NotImplementedError


if __name__ == "__main__":
    print(b''.join(download_file('http://scripts.mit.edu/~6.009/lab6/redir.py/0/cat_poster.jpg.parts')))
