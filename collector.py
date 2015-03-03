from os import listdir, remove
from shutil import rmtree
from utils import load_json, call, check_skip, create_dir, extract, move
import json
import re

config = load_json('cdn-config.json')

print 'Rebuild CDN collection.'

for target in config['targets']:
    print 'Collect %s libraries.' % target

    create_dir("%s/%s" % (config['directory'], target))

    lib_info = call("bower info %s -j --allow-root" % target)
    if not lib_info:
        print '[ERROR] Cannot collect information about library'
        break

    versions = [
        version for version in json.loads(lib_info)['versions']
        if not check_skip(version, config['skipWords'])
    ]

    for version in versions:
        target_directory = "%s/%s/%s" % (config['directory'], target, version)
        if not create_dir(target_directory) and listdir(target_directory):
            print '[DEBUG] Version %s#%s: Already exists' % (target, version)
            continue

        info = call("bower install %s#%s -j --allow-root" % (target, version), True)

        tmp_directory = 'tmp'
        if listdir('tmp'):
            tmp_directory = "%s/%s" % (tmp_directory, listdir(tmp_directory)[0])
            move(listdir(tmp_directory), tmp_directory, target_directory)
            print '[INFO] Version %s#%s: Downloaded' % (target, version)
            rmtree(tmp_directory)

call('tree %(d)s -d -L 2 | grep -v %(d)s | grep -v directories > %(d)s/cdn.description' % {'d': config['directory']})
