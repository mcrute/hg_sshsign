# vim:filetype=python:fileencoding=utf-8
import os
import tempfile
import subprocess


def make_test_repo():
    tmpdir = tempfile.mkdtemp('.tmp', __name__.replace('.', '_'))

    os.chdir(tmpdir)
    subprocess.call('hg init test-repo.hg', shell=True)
    os.chdir('test-repo.hg')

    for filename, text, is_new, message in SKEL_FILES:
        write_commit_file(filename, is_new=is_new, text=text, message=message)

    return tmpdir, os.path.join(tmpdir, 'test-repo.hg')


def write_commit_file(filename, is_new=True, text='', message=''):
    handle = open(filename, 'w')
    handle.write(text)
    handle.close()

    if is_new:
        subprocess.call('hg add %s' % filename, shell=True)

    subprocess.call('hg ci -m %r %s' % (message, filename),
                    shell=True)


SKEL_FILES = (
    ('foo', 'bar', True, 'this is my foo'),
    ('ham', 'bones', True, 'this is my ham'),
    ('qwx', 'schnizzle', True, 'this is for testing'),
    ('foo', 'bar\npatoot', False, 'my foo. it grows.'),
    ('ham', 'booones', False, 'this ham is better'),
    ('qwx', '', False, 'I grew tired of this qwx'),
)
