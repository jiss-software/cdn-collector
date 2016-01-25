from os import listdir, remove, path
from shutil import rmtree
from utils import load_json, call, check_skip, check_pattern, create_dir, move
import json

config = load_json('cdn-config.json')

print '[INFO] Rebuild CDN collection.'

for target, pattern in config['targets']:
    print '[INFO] Collect %s libraries.' % target
    target_dir = target[target.find('/') + 1:] if target.find('/') > 0 else target

    create_dir("%s/%s" % (config['directory'], target_dir))

    lib_info = call("bower info %s -j --allow-root" % target)
    if not lib_info:
        print '[ERROR] Cannot collect information about library'
        break

    versions = [
        version for version in json.loads(lib_info)['versions']
        if not check_skip(version, config['skipWords']) and check_pattern(version, pattern)
    ]

    for version in versions:
        target_directory = "%s/%s/%s" % (config['directory'], target_dir, version)
        if not create_dir(target_directory) and listdir(target_directory):
            print '[DEBUG] Version %s#%s: Already exists' % (target, version)
            continue

        call("bower install %s#%s -j --allow-root --force-latest --production" % (target, version), True)

        tmp_directory = "tmp/%s" % target_dir
        if path.isdir(tmp_directory):
            move(listdir(tmp_directory), tmp_directory, target_directory)
            print '[INFO] Version %s#%s: Downloaded' % (target, version)
            rmtree(tmp_directory)
        else:
            print '[ERROR] Cannot download %s#%s' % (target, version)
            
remove('%s/cdn.description' % config['directory'])
call('tree %(d)s -d -L 2 | grep -v %(d)s | grep -v directories > %(d)s/cdn.description' % {'d': config['directory']})
