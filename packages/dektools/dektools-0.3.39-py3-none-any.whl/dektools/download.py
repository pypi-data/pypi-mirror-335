import os
from .file import sure_parent_dir, remove_path, normal_path
from .shell import shell_wrapper, shell_exitcode
from .web.url import Url
from .func import FuncAnyArgs


def download_http_exist(url, username=None, password=None):
    url = Url.new(url)
    url.update(username=username, password=password)
    if os.name == 'nt':
        command = f'powershell -Command "Invoke-WebRequest -Method Head {url.value}"'
    else:
        command = f"curl --output /dev/null --silent --head --fail {url}"
    return shell_exitcode(command) == 0


def download_from_http(url, path=None, username=None, password=None):
    url = Url.new(url)
    url.update(username=username, password=password)
    if path is None:
        path = os.path.join(os.getcwd(), url.filename)
    elif callable(path):
        path = FuncAnyArgs(path)(url.filename)
    path = normal_path(path)
    sure_parent_dir(path)
    remove_path(path)
    if os.name == 'nt':
        shell_wrapper(f'powershell -Command "Invoke-WebRequest -OutFile {path} {url.value}"')
    else:
        shell_wrapper(f'curl -fLSs {url.value} -o {path}')
    return path


def download_from_git(url, path):  # http://localhost/path/.git+my-branch
    url = Url.new(url)
    if path is None:
        path = os.path.join(os.getcwd(), url.dirname)
    elif callable(path):
        path = FuncAnyArgs(path)(url.dirname)
    path = normal_path(path)
    sure_parent_dir(path)
    remove_path(path)
    ul = url.split('+', 1)
    b = []
    if len(ul) > 1:
        b = ['-b', ul[1]]
    sub = ' '.join([*b, ul[0]])
    shell_wrapper(f'git -C {os.path.dirname(path)} clone {sub} {os.path.basename(path)}')
    return path


def download_tree_from_http(path, url_list, username=None, password=None):
    result = {}
    for url in url_list:
        result[url] = download_from_http(url, lambda f: os.path.join(path, f), username, password)
    return result


def curl_auth_args(username=None, password=None):
    auth = ''
    if username:
        auth += f' -u {username}'
        if password:
            auth += f':{password}'
    return auth
