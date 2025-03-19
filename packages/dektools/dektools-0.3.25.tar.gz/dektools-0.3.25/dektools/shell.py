import os
import sys
import json
import time
import shlex
import shutil
import functools
import subprocess
from .file import write_file, remove_path
from .dict import list_dedup, is_list
from .escape import shell_quote


def shell_wrapper(command, check=True, chdir=None, env=None):
    dir_last = None
    if chdir:
        dir_last = os.getcwd()
        os.chdir(chdir)
    err = subprocess.call(shell_quote(command), shell=True, env=env)  # equals to bash -c '<command>'
    if check and err:
        if dir_last:
            os.chdir(dir_last)
        raise ChildProcessError(command)
    if dir_last:
        os.chdir(dir_last)
    return err


def shell_retry(command, times=None, notify=True, env=None):
    count = 0
    while True:
        if isinstance(command, str):
            err = subprocess.call(shell_quote(command), shell=True, env=env)
        else:
            try:
                err = command() or 0
            except ChildProcessError:
                err = 1
        if err:
            count += 1
            if times is not None and count >= times:
                raise ChildProcessError(command)
            if notify:
                sys.stdout.write(f"shell_retry<{count}>: {command}\n")
                sys.stdout.flush()
            time.sleep(0.1)
        else:
            break


def shell_output(command, error=True, env=None, encode=None):
    return shell_result(command, error, env, encode)[1]


def shell_exitcode(command, error=True, env=None, encode=None):
    return shell_result(command, error, env, encode)[0]


def shell_result(command, error=True, env=None, encode=None):
    return getstatusoutput(command, error, env, encode)


def getstatusoutput(command, error=True, env=None, encode=None):
    try:
        data = subprocess.check_output(
            shell_quote(command), shell=True, env=env,
            stderr=subprocess.STDOUT if error else subprocess.DEVNULL)
        exitcode = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    data = data.decode(encode or 'utf-8')
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data


def shell_with_input(command, inputs, env=None):
    p = subprocess.Popen(
        shlex.split(command), env=env, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if isinstance(inputs, str):
        inputs = inputs.encode('utf-8')
    outs, errs = p.communicate(input=inputs)
    return p.returncode, outs, errs


def shell_stdout(command, write=None, env=None):
    proc = subprocess.Popen(shell_quote(command),
                            env=env,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True
                            )
    write = write or sys.stdout.write
    while proc.poll() is None:
        stdout = proc.stdout.readline()
        write(stdout)


def shell_tee(command, env=None):
    def write(s):
        nonlocal result
        result += s
        sys.stdout.write(s)

    result = ''
    shell_stdout(command, write=write, env=env)
    return result


def shell_command(command, sync=True, headless=False, quiet=False, ignore=False, env=None):
    result = None
    if os.name == 'nt' and headless:
        result = shell_command_nt_headless(command, sync)
    else:
        if not sync:
            command = _cmd_to_async(command)
        if quiet:
            shell_output(command)
        else:
            try:
                subprocess.run(shell_quote(command), check=True, shell=True, env=env)
            except subprocess.CalledProcessError as e:
                result = ChildProcessError((command, e))
    return None if ignore else result


def _cmd_to_async(command):
    if os.name == 'nt':
        command = 'start ' + command
    else:
        command = 'nohup ' + command + ' &'
    return command


def shell_command_nt_headless(command, sync=True, env=None):
    executor = 'wscript'
    if not env:
        env = os.environ.copy()
    marker = __name__.partition(".")[0].upper() + '_VBS_ENV'
    if env.get(marker) == 'true':  # As vbs call deep bug
        if sync:
            return shell_command(command, sync, headless=False, env=env)
        else:
            executor = 'start ' + executor
    env[marker] = "true"

    vbs = f"""
Dim Wsh
Set Wsh = WScript.CreateObject("WScript.Shell")
Wsh.Run "{shell_quote(command)}",0,{'true' if sync else 'false'}
Set Wsh=NoThing
WScript.quit
    """
    fp = write_file('run.vbs', s=vbs, t=True)
    try:
        subprocess.run(f'{executor} {fp}', check=True, shell=True, env=env)
    except subprocess.CalledProcessError as e:
        return e
    return None


def shell_command_nt_as_admin(command, env=None):
    executor = 'wscript'
    if not env:
        env = os.environ.copy()
    cs = shlex.split(command, posix=False)
    exe = cs[0]
    params = ' '.join(cs[1:])
    vbs = f"""
Dim Wsh
Set Wsh = WScript.CreateObject("Shell.Application")
Wsh.ShellExecute "{exe}", "{params}", , "runas", 1
Set Wsh=NoThing
WScript.quit
    """
    fp = write_file('run.vbs', s=vbs, t=True)
    try:
        subprocess.run(f'{executor} {fp}', check=True, shell=True, env=env)
    except subprocess.CalledProcessError as e:
        return e
    finally:
        remove_path(fp)
    return None


def show_win_msg(msg=None, title=None):
    if os.name == 'nt':
        import ctypes
        mb = ctypes.windll.user32.MessageBoxW
        mb(None, msg or 'Message', title or 'Title', 0)


class Cli:
    def __init__(self, list_or_dict, path=None):
        if is_list(list_or_dict):
            self.recon = {k: None for k in list_or_dict}
        else:
            self.recon = list_or_dict
        self.path = path

    @property
    @functools.lru_cache(None)
    def cur(self):
        if self.path:
            bin_list = [k for k, v in self.recon.items() if not v or os.path.exists(os.path.join(self.path, v))]
        else:
            bin_list = []
        bin_list = list_dedup([*bin_list, *self.recon])
        for cli in bin_list:
            if shutil.which(cli):
                return cli


def output_data(data, out=None, fmt=None, prefix=None):
    if prefix:
        data = {f"{prefix}{k}": v for k, v in data.items()}
    fmt = fmt or 'env'
    if fmt == 'env':
        s = "\n".join(f'{k}="{v}"' for k, v in data.items())
    elif fmt == 'json':
        s = json.dumps(data)
    elif fmt == 'yaml':
        from .yaml import yaml
        s = yaml.dumps(data)
    else:
        raise TypeError(f'Please provide a correct format: {fmt}')
    if out:
        write_file(out, s=s)
    else:
        out = write_file(f'.{fmt}', s=s, t=True)
        sys.stdout.write(out)


def get_current_sys_exe():
    return shutil.which(os.path.basename(sys.argv[0]))


def associate(ext, filetype, command):
    shell_wrapper(f"assoc {ext}={filetype}")
    shell_wrapper(f"ftype {filetype}={command}")


def associate_remove(ext, filetype):
    shell_wrapper(f"ftype {filetype}=")
    shell_wrapper(f"assoc {ext}=")


def associate_console_script(ext, _name_, sub, content, is_code=False):
    name = _name_.partition('.')[0]
    if is_code:
        path_pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        command = fr'''"{path_pythonw}" -c "{content}"'''
    else:
        command = fr'''"{get_current_sys_exe()}" {content} "%1" %*'''
    associate(ext, f"Python.ConsoleScript.{name}.{sub}", command)


def associate_console_script_remove(ext, _name_, sub):
    name = _name_.partition('.')[0]
    associate_remove(ext, f"Python.ConsoleScript.{name}.{sub}")
