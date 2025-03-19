from distutils.spawn import find_executable
import os
import subprocess

from pybsc.makedirs import makedirs

_search_path = os.environ['PATH']
_git_executable = find_executable('git', path=_search_path)

exists = _git_executable is not None


def is_under_git_control():
    """Checking under git control

    Returns
    -------
    ret : bool
        result of under git control.
    """
    if not exists:
        return False
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(['git', 'rev-parse'], stdout=FNULL, stderr=FNULL)
    except subprocess.CalledProcessError:
        return False
    return True


def touch_gitignore(outpath):
    makedirs(outpath)
    with open(os.path.join(str(outpath), '.gitignore'), 'w') as f:
        f.write('*\n')
