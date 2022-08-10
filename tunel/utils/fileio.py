__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import errno
import hashlib
import json
import os
import re
import shutil
import tempfile

import yaml

from tunel.logger import logger


def mkdirp(dirnames):
    """
    Create one or more directories
    """
    for dirname in dirnames:
        mkdir_p(dirname)


def mkdir_p(path):
    """mkdir_p attempts to get the same functionality as mkdir -p
    :param path: the path to create.
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            logger.exit("Error creating path %s, exiting." % path)


def get_tmpfile(tmpdir=None, prefix=""):
    """
    Get a temporary file with an optional prefix.
    """
    # First priority for the base goes to the user requested.
    if not tmpdir:
        tmpdir = get_tmpdir(tmpdir)

    # If tmpdir is set, add to prefix
    if tmpdir:
        prefix = os.path.join(tmpdir, os.path.basename(prefix))

    fd, tmp_file = tempfile.mkstemp(prefix=prefix)
    os.close(fd)

    return tmp_file


def get_tmpdir(tmpdir=None, prefix="", create=True):
    """
    Get a temporary directory for an operation.
    """
    tmpdir = tmpdir or tempfile.gettempdir()
    prefix = prefix or "tunel-tmp"
    prefix = "%s.%s" % (prefix, next(tempfile._get_candidate_names()))
    tmpdir = os.path.join(tmpdir, prefix)

    if not os.path.exists(tmpdir) and create is True:
        os.mkdir(tmpdir)

    return tmpdir


def recursive_find(base, pattern=None):
    """
    Find filenames that match a particular pattern, and yield them.
    """
    # We can identify modules by finding module.lua
    for root, folders, files in os.walk(base):
        for file in files:
            fullpath = os.path.abspath(os.path.join(root, file))

            if pattern and not re.search(pattern, fullpath):
                continue

            yield fullpath


def get_file_hash(image_path, algorithm="sha256"):
    """
    Return an sha256 hash of the file based on a criteria level.
    """
    try:
        hasher = getattr(hashlib, algorithm)()
    except AttributeError:
        logger.error("%s is an invalid algorithm.")
        logger.exit(" ".join(hashlib.algorithms_guaranteed))

    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def copyfile(source, destination, force=True):
    """
    Copy a file from a source to its destination.
    """
    # Case 1: It's already there, we aren't replacing it :)
    if source == destination and force is False:
        return destination

    # Case 2: It's already there, we ARE replacing it :)
    if os.path.exists(destination) and force is True:
        os.remove(destination)

    shutil.copyfile(source, destination)
    return destination


def write_file(filename, content, mode="w"):
    """
    Write content to a filename
    """
    with open(filename, mode) as filey:
        filey.writelines(content)
    return filename


def write_json(json_obj, filename, mode="w", print_pretty=True):
    """Write json to a filename"""
    with open(filename, mode) as filey:
        if print_pretty:
            filey.writelines(print_json(json_obj))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename


def print_json(json_obj):
    """Print json pretty"""
    return json.dumps(json_obj, indent=4, separators=(",", ": "))


def read_file(filename, mode="r"):
    """Read a file."""
    with open(filename, mode) as filey:
        content = filey.read()
    return content


def read_yaml(filename):
    """
    Read yaml from file
    """
    with open(filename, "r") as fd:
        content = yaml.load(fd.read(), Loader=yaml.SafeLoader)
    return content


def read_lines(filename):
    """
    Given a file with multple lines, read into a list
    """
    content = read_file(filename)
    return [x for x in content.split("\n") if x]


def read_config_file(filename, sep="="):
    """
    Given a config file with format KEY = VALUE, parse into dict
    """
    cfg = {}
    for line in read_file(filename).split("\n"):
        if sep not in line:
            continue
        key, val = line.split(sep, 1)
        cfg[key.strip()] = val.strip()
    return cfg


def read_json(filename, mode="r"):
    """Read a json file to a dictionary."""
    return json.loads(read_file(filename))
