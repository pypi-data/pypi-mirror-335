import os
import sys
import random
import time
import string
from urllib3 import PoolManager, ProxyManager, make_headers
from urllib3.exceptions import HTTPError
from dektools.file import write_file, sure_dir, remove_path, normal_path
from dektools.web.url import Url
from dektools.format import format_file_size
from dektools.web.status import HTTP_200_OK
from dektools.func import FuncAnyArgs


def _get_url(url, username, password):
    url = Url.new(url)
    if username and password:
        url.update(username=username, password=password)
    return url


def _get_manager(proxy):
    if proxy:
        url = Url.new(proxy)
        proxy_headers = None
        if url.username and url.password:
            proxy_headers = make_headers(proxy_basic_auth=f'{url.username}:{url.password}')
            url.update(username=None, password=None)
        http = ProxyManager(url.value, proxy_headers=proxy_headers)
    else:
        http = PoolManager()
    return http


def download_exist(url, username=None, password=None, proxy=None):
    url = _get_url(url, username, password)
    with _get_manager(proxy) as http:
        try:
            with http.request('GET', url.value, preload_content=False, decode_content=False) as rsp:
                return rsp.status == HTTP_200_OK
        except HTTPError:
            pass
    return False


def download_file(
        url, path=None, username=None, password=None, retries=None, proxy=None, interval=0.5, block_size=6 * 1024):
    url = _get_url(url, username, password)
    if path is None:
        path = os.path.join(os.getcwd(), url.filename)
    elif callable(path):
        path = FuncAnyArgs(path)(url.filename)
    path = normal_path(path)
    filename = os.path.basename(path)
    while True:
        random_name = ''.join(random.choice(string.hexdigits) for _ in range(16))
        path_target_temp = f"{path}.{random_name}"
        if not os.path.exists(path_target_temp):
            break
    times = 0
    while retries is None or times <= retries:
        if times:
            sys.stdout.write(f'Download retrying: {times}\n')
        try:
            with _get_manager(proxy) as http:
                with http.request('GET', url.value, preload_content=False, decode_content=False) as rsp:
                    if rsp.status != HTTP_200_OK:
                        if times > 0:
                            times += 1
                            time.sleep(1)
                            continue
                        else:
                            raise HTTPError(f'Download({url.value}) error status {rsp.status}')
                    cursor_size = 0
                    full_size = rsp.headers.get('content-length')
                    if full_size:
                        full_size = int(full_size)
                    sure_dir(os.path.dirname(path_target_temp))
                    with open(path_target_temp, 'wb') as f:
                        f.truncate()
                        ts = time.time()
                        for chunk in rsp.stream(block_size):
                            if time.time() - ts > interval:
                                ts = time.time()
                                if full_size:
                                    sys.stdout.write(
                                        '\rDownloading [%s]: %.2f%%' % (filename, cursor_size * 100 / full_size))
                                else:
                                    sys.stdout.write('\rDownloading [%s]: %s' % (
                                        filename, format_file_size(cursor_size)))
                            cursor_size += len(chunk)
                            f.write(chunk)
                        # Add this as no error raised when connection closed
                        with http.request('GET', url.value, preload_content=False, decode_content=False):
                            pass
                        times = 0
                        sys.stdout.write('\rDownloaded [%s]: %s\n' % (filename, format_file_size(cursor_size)))
        except HTTPError as e:
            sys.stderr.write(f'\nDownload error: {e.__class__.__name__}: {e.args}\n')
            times += 1
            time.sleep(1)
        else:
            break
    if times > 0:
        remove_path(path_target_temp)
        raise HTTPError('Download failed') from None
    remove_path(path)
    write_file(path, m=path_target_temp)
    return path


def download_dir(path, url_list, username=None, password=None):
    result = {}
    for url in url_list:
        result[url] = download_file(url, lambda f: os.path.join(path, f), username, password)
    return result
