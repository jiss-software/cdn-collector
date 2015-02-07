import os
from subprocess import Popen, PIPE
import tarfile
import json
import shutil
import re


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

    proc = Popen(["bower info %s" % target], stdout=PIPE, shell=True)

    start = False
    for line in proc.communicate()[0].splitlines():
        if not start:
            if 'Available versions:' in line:
                start = True

            continue

        if 'You can request' in line:
            break

        if check_skip(line, config['skipWords']):
            continue

        version = line.strip()[2:]
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

        proc_info = Popen(["bower info %s#%s" % (target, version)], stdout=PIPE, shell=True)
        link = None

        info = proc_info.communicate()[0]
        info = info[info.find('{'):info.rfind('}') + 1].replace(': ', '": ')
        for i, match in enumerate(re.finditer('( [A-za-z]+":)', info)):
            pos = match.start() + 1 + i
            info = info[:pos] + '"' + info[pos:]

        info = info.replace('\'', '"')
        info = json.loads(info)

        if info['homepage']:
            wget_cmd = 'wget --directory-prefix="%(target)s/%(version)s" "%(link)s/archive/%(version)s.tar.gz"' % {
                'target': target,
                'version': version,
                'link': info['homepage']
            }

            print wget_cmd
            proc_download = Popen([wget_cmd], stdout=PIPE, shell=True)
            print proc_download.communicate()[0]

            archive = "%s/%s" % (directory, os.listdir(directory)[0])
            tfile = tarfile.open(archive, 'r:gz')
            tfile.extractall(directory)
            os.remove(archive)

            location = "%s/%s" % (directory, os.listdir(directory)[0])
            move(info.get('main', info.get('scripts')), location, directory)

            shutil.rmtree(location)
        else: 
            print 'Download link for version not found.'
            print info
