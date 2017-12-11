#!/usr/bin/env python
#encoding: utf-8

""" Python Code Protector """

import os
import sys
import imp
import marshal
import traceback

import _pyprotect

MAGIC = imp.get_magic()

# recurse dir
m_recurse = True

# delete after protect
m_delete = False

# follow symlink
m_symlink = True


def wr_long(f, x):
    """Internal; write a 32-bit int to a file in little-endian order."""
    f.write(chr( x        & 0xff))
    f.write(chr((x >> 8)  & 0xff))
    f.write(chr((x >> 16) & 0xff))
    f.write(chr((x >> 24) & 0xff))


def protect_file(file, cfile=None):
    """ Protect a pyfile """
    if os.path.islink(file) and not m_symlink:
        print 'Protect: ignore symlink file:', file
        return True

    if not os.path.isfile(file):
        return False

    if file.endswith(".pyc") or file.endswith(".pyo"):
        return False

    if not file.endswith(".py"):
        print 'Protect: ignore non-py file:', file
        return True

    f = open(file, 'U')
    try:
        timestamp = long(os.fstat(f.fileno()).st_mtime)
    except AttributeError:
        timestamp = long(os.stat(file).st_mtime)
    codestring = f.read()
    f.close()
    if codestring and codestring[-1] != '\n':
        codestring = codestring + '\n'

    try:
        os.putenv('PYTHONOPTIMIZE', '2')
        codeobject = compile(codestring, file, 'exec')
    except:
        traceback.print_exc()
        return False

    _pyprotect.protect(codeobject)

    if cfile is None:
        cfile = file + (__debug__ and 'c' or 'o')

    fc = open(cfile, 'wb')
    fc.write('\0\0\0\0')
    wr_long(fc, timestamp)
    marshal.dump(codeobject, fc)
    fc.flush()
    fc.seek(0, 0)
    fc.write(MAGIC)
    fc.close()

    if m_delete:
        try:
            os.unlink(file)
        except Exception, e:
            print 'Protect: failed to delete file: %s, reason: %s' % (file,
                    str(e))

    return True


def protect_dir(dirname):
    """ Protect py files in a dir 
    
    """
    for dirname, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            fullname = os.path.join(dirname, filename)
            protect_file(fullname)

        if not m_recurse:
            break


def protect(filenames):
    """ Protect file or dirs """
    
    for filename in filenames:
        if os.path.isfile(filename):
            protect_file(filename)
        elif os.path.isdir(filename):
            protect_dir(filename)
        else:
            print 'Unknown file type:', filename


def parse_cmdline():
    """ Parse command line 
    
    """
    from optparse import OptionParser
    global m_recurse, m_delete, m_symlink

    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option('-R', dest='recurse', default=None, action='store_true',
            help='Protect all .py in the dir and subdirs')
    parser.add_option('--delete', default=None, action='store_true',
            help='Delete origin .py file after protect')
    parser.add_option('--symlink', default=None, action='store_true',
            help='Follow symlink file')

    opts, args = parser.parse_args()

    m_recurse = opts.recurse
    m_delete  = opts.delete
    m_symlink = opts.symlink

    return args


if __name__ == '__main__':
    filenames = parse_cmdline()

    if not filenames:
        print 'Usage: pyprotect [-R] [--delete] file|dir'
        sys.exit(0)

    protect(filenames)

