from subprocess import Popen, PIPE
import json
import shutil
import re
import os
import tarfile
import semver


def extract(archive, directory):
    tfile = tarfile.open(archive, 'r:gz')
    tfile.extractall(directory)


def create_dir(target):
    if not os.path.isdir(target):
        os.mkdir(target)
        return True

    return False


def call(cmd, err=False):
    result = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()

    if err:
        return result

    if not result[0] and result[1]:
        print result[1]
        return None

    return result[0]


def move(target, origin, destination):
    if not target:
        return

    if not isinstance(target, basestring):
        for entry in target:
            move(entry, origin, destination)

        return

    target = target.replace('/*', '')

    destination_path = '%s/%s' % (destination, re.sub('(\./|bin/|dist/|release/)', '', target))
    origin_path = '%s/%s' % (origin, re.sub('(\./)', '', target))

    try:
        os.makedirs(os.path.dirname(destination_path))
    except os.error:
        pass

    try:
        shutil.move(origin_path, destination_path)
    except Exception as error:
        print error.message


def load_json(conf):
    json_data = open(conf)
    data = json.load(json_data)
    json_data.close()

    return data


def check_skip(text, skips):
    text = text.lower()
    for word in skips:
        if word in text:
            return True

    return False


def check_pattern(text, pattern):
    return pattern == '*' or semver.match(text, pattern)
