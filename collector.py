import os
from subprocess import Popen, PIPE
import tarfile
import json
import shutil
import re


def call(cmd):
    return Popen([cmd], stdout=PIPE, shell=True).communicate()[0]


def move(file, origin, destination):
    if not file:
        return

    if not isinstance(file, basestring):
        for entry in file:
            move(entry, origin, destination)

        return

    destination_path = '%s/%s' % (destination, re.sub('(\./|bin/|dist/)', '', file))
    origin_path = '%s/%s' % (origin, re.sub('(\./)', '', file))

    shutil.move(origin_path, destination_path)


def load_json(conf):
    json_data = open(conf)
    data = json.load(json_data)
    json_data.close()

    return data


def check_skip(text, skips):
    for word in skips:
        if word in text:
            return True

    return False

config = load_json('cdn-config.json')

print 'Rebuild CDN collection.'

for target in config['targets']:
    print 'Collect %s libraries.' % target

    lib_info = call("bower info %s -j" % target)
    print lib_info
    lib_info = lib_info[lib_info.rfind('}]'):]

    print "XXXXXXXXX" + str(lib_info.rfind('}\]'))
    print lib_info

    break
    versions = [
        version for version in json.loads(lib_info)['versions']
        if not check_skip(version, config['skipWords'])
    ]

    for version in versions:
        print 'Version found %s - %s.' % (target, version)

        if not os.path.isdir(target):
            os.mkdir(target)

        directory = "%s/%s" % (target, version)
        if os.path.isdir(directory):
            if os.listdir(directory):
                print 'Skip version, directory already exists %s/%s' % (target, version)
                continue
        else:
            os.mkdir("%s/%s" % (target, version))

        info = call("bower info %s#%s -j" % (target, version))
        info = json.loads(info[info.rfind('}]') + 2:])

        link = None
        for entry in info:
            if entry["id"] is "download":
                link = entry["message"]
                break

        if not link:
            link = 'http/%s/archive/%s.tar.gz' % (
                re.finditer('git://(.c*)\.git', info[0]["message"]).next().groups()[0], version
            )

        print call('wget --directory-prefix="%s" "%s"' % (directory, link))

        #if os.listdir(directory):
        #    archive = "%s/%s" % (directory, os.listdir(directory)[0])
        #    tfile = tarfile.open(archive, 'r:gz')
        #    tfile.extractall(directory)
        #    os.remove(archive)

        #    location = "%s/%s" % (directory, os.listdir(directory)[0])
        #    move(info.get('min', info.get('scripts')), location, directory)

        #    shutil.rmtree(location)
