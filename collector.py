from os import listdir, remove
from shutil import rmtree
from utils import load_json, call, check_skip, create_dir, extract, move
import json
import re

config = load_json('cdn-config.json')

print 'Rebuild CDN collection.'

for target in config['targets']:
    print 'Collect %s libraries.' % target

    create_dir(target)

    lib_info = call("bower info %s -j" % target)
    if not lib_info:
        print 'Cannot collect information about library'
        break

    versions = [
        version for version in json.loads(lib_info)['versions']
        if not check_skip(version, config['skipWords'])
    ]

    for version in versions:
        print 'Version found %s - %s.' % (target, version)

        directory = "%s/%s" % (target, version)
        if not create_dir(directory) and listdir(directory):
            print 'Skip version, directory already exists %s/%s and not empty' % (target, version)
            continue

        info = call("bower info %s#%s -j" % (target, version), True)

        if info[0]:
            files = json.loads(info[0])
            files = files.get('main', files.get('scripts'))
        else:
            files = None

        info = json.loads(info[1])

        link = None
        for entry in info:
            if entry["id"] is "download":
                link = entry["message"]
                break

        if not link:
            tag_name = None

            if 'data' in info[0] and 'pkgMeta' in info[0]['data']:
                if '_resolution' in info[0]['data']['pkgMeta'] and 'tag' in info[0]['data']['pkgMeta']['_resolution']:
                    tag_name = info[0]['data']['pkgMeta']['_resolution']['tag']

            tag_name = version if not tag_name else tag_name

            link = '%s/archive/%s.tar.gz' % (re.sub('(git://|\.git.*)', '', info[0]["message"]), tag_name)

        print call('wget --directory-prefix="%s" "%s"' % (directory, link))

        if listdir(directory):
            archive = "%s/%s" % (directory, listdir(directory)[0])
            extract(archive, directory)
            remove(archive)

            location = "%s/%s" % (directory, listdir(directory)[0])
            move(files if files else listdir(location), location, directory)

            rmtree(location)