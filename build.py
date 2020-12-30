import argparse
import glob
import json
import os
import shutil
import sys
import urllib.request

import config
import util


def parse_args():
    parser = argparse.ArgumentParser()

    revision = parser.add_mutually_exclusive_group(required=True)
    revision.add_argument('--last', action='store_true')
    revision.add_argument('--branch', type=str, action='store')

    parser.add_argument('--cpu', type=str, action='store', required=True)
    parser.add_argument('--os', type=str, action='store', required=True)

    ssl = parser.add_mutually_exclusive_group()
    ssl.add_argument('--boringssl', type=str, action='store')
    ssl.add_argument('--build-boringssl', action='store_true')

    parser.add_argument('--no-cubbit', action='store_true')
    parser.add_argument('--no-log', action='store_true')
    parser.add_argument('--rtti', action='store_true')

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--debug-only', action='store_true')
    mode.add_argument('--release-only', action='store_true')

    parser.add_argument('--no-archive', action='store_true')
    parser.add_argument('--specific-out-dir', action='store_true')

    return parser.parse_args()


def fetch_last(args, conf):
    chromium_releases = json.loads(urllib.request.urlopen(
        'https://chromiumdash.appspot.com/fetch_milestones').read())
    conf['branch'] = chromium_releases[0]['webrtc_branch']

    #if not args.build_boringssl:
    #    conf['boringssl'] = 'master-with-bazel'

    return conf


def retrieve_commit(conf):
    util.cd(util.getpath(config.PATH_WEBRTC, 'src'))
    conf['webrtc_commit'] = util.exec_stdout('git', 'log', '--format="%H"', '-n', '1').decode("utf-8").strip().strip("\"")

    if conf['boringssl']:
        util.cd(util.getpath(config.PATH_BORINGSSL))
        conf['boringssl_commit'] = util.exec_stdout('git', 'log', '--format="%H"', '-n', '1').decode("utf-8").strip().strip("\"")

    return conf


def parse_conf(args):
    conf = {}

    conf['cpu'] = args.cpu
    conf['os'] = args.os

    conf['boringssl'] = args.boringssl

    conf['cubbit'] = not bool(args.no_cubbit)
    conf['no_log'] = bool(args.no_log)
    conf['rtti'] = bool(args.rtti)

    if args.debug_only:
        conf['mode'] = ['debug']
    elif args.release_only:
        conf['mode'] = ['release']
    else:
        conf['mode'] = ['debug', 'release']

    conf['no_archive'] = bool(args.no_archive)
    conf['specific_out_dir'] = bool(args.specific_out_dir)

    if args.last:
        conf = fetch_last(args, conf)
    else:
        conf['branch'] = args.branch

    return retrieve_commit(conf)


def setup(conf):
    util.cd(config.DIR_BUILD)
    if os.path.exists(util.getpath(config.PATH_DEPOT_TOOLS)):
        util.cd(config.PATH_DEPOT_TOOLS)
        util.exec('git', 'checkout', '-f', 'master')
        util.exec('git', 'pull')
    else:
        util.exec('git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git',
                  util.getpath(config.PATH_DEPOT_TOOLS))

    os.environ['PATH'] = util.getpath(
        config.PATH_DEPOT_TOOLS) + os.path.pathsep + os.environ['PATH']

    if sys.platform == 'win32':
        os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'

    if conf['boringssl']:
        if os.path.exists(util.getpath(config.PATH_BORINGSSL)):
            util.cd(config.PATH_BORINGSSL)
            util.exec('git', 'reset', '--hard')
            util.exec('git', 'fetch', '--all')
        else:
            util.exec('git', 'clone', 'https://boringssl.googlesource.com/boringssl.git',
                      util.getpath(config.PATH_BORINGSSL))

        util.cd(config.PATH_BORINGSSL)
        util.exec('git', 'checkout', '-f', conf['boringssl'])

        if os.path.exists(util.getpath(config.PATH_BORINGSSL, 'src', 'include')):
            conf['boringssl_path'] = util.getpath(
                config.PATH_BORINGSSL, 'src', 'include')
        elif os.path.exists(util.getpath(config.PATH_BORINGSSL, 'src')):
            conf['boringssl_path'] = util.getpath(config.PATH_BORINGSSL, 'src')
        else:
            conf['boringssl_path'] = util.getpath(config.PATH_BORINGSSL)


def pull(conf):
    webrtc_path = util.getpath(config.PATH_WEBRTC)

    util.cd(webrtc_path)
    if not util.exists(webrtc_path, '.gclient'):
        os.rmdir(util.getpath(config.PATH_WEBRTC, 'src'))
        util.exec('fetch', '--nohooks', 'webrtc')

    util.cd(webrtc_path, 'src')

    util.exec('git', 'reset', '--hard')
    util.exec('git', 'fetch', 'origin')
    util.exec('git', 'checkout', "{}{}".format(
        config.WEBRTC_BRANCH_PREFIX, conf["branch"]))

    util.exec('gclient', 'sync', '-D')


# def patch(conf):
#     webrtc_src_path = util.getpath(config.PATH_WEBRTC, 'src')

#     if conf['no_log']:
#         log_file = os.path.join(
#             webrtc_src_path, 'rtc_base{}logging.cc'.format(os.path.sep))
#         with open(log_file, 'r') as file:
#             filedata = file.read()
#         filedata = filedata.replace(
#             'LoggingSeverity g_min_sev = LS_INFO', 'LoggingSeverity g_min_sev = LS_NONE')
#         filedata = filedata.replace(
#             'LoggingSeverity g_dbg_sev = LS_INFO', 'LoggingSeverity g_dbg_sev = LS_NONE')
#         with open(log_file, 'w') as file:
#             file.write(filedata)


def _generate_args(conf, mode):
    args = []

    args.append('target_os="{}"'.format(conf['os']))
    args.append('target_cpu="{}"'.format(conf['cpu']))

    if conf['cubbit']:
        args = args + config.cubbit_default['gn_args']

    if mode == 'debug':
        args.append('is_debug=true')
        args.append('enable_iterator_debugging=true')
        args.append('use_debug_fission=false')
    else:
        args.append('is_debug=false')

    if conf['no_log']:
        args.append('rtc_disable_logging=true')

    if conf['rtti']:
        args.append('use_rtti=true')
    else:
        args.append('use_rtti=false')

    if conf['boringssl']:
        args.append('rtc_build_ssl=false')
        args.append('rtc_ssl_root="{}"'.format(conf['boringssl_path']))
    else:
        args.append('rtc_build_ssl=true')

    if conf['os'] == 'win':
        args.append('is_clang=false')

    args.append('use_custom_libcxx=false')

    return args


def _generate_name(conf, mode=None):
    separator = '-'
    name = 'webrtc_{}'.format(conf['webrtc_commit'][:8])

    name = separator.join([name, conf["branch"]])

    name = separator.join([name, conf['os']])
    name = separator.join([name, conf['cpu']])

    if conf['cubbit']:
        name = separator.join([name, 'cubbit'])

    if conf['rtti']:
        name = separator.join([name, 'rtti'])

    if conf['boringssl']:
        name = separator.join(
            [name, 'boringssl_{}'.format(conf['boringssl_commit'][:8])])

    if conf['no_log']:
        name = separator.join([name, 'nolog'])

    if mode:
        if mode == 'debug':
            name = separator.join([name, 'debug'])
        else:
            name = separator.join([name, 'release'])

    return name


def _generate_out(conf, mode):
    if(conf['specific_out_dir']):
        name = _generate_name(conf, mode)
    else:
        name = 'default'

    return 'out/{}'.format(name)


def build(conf, mode):
    webrtc_src_path = util.getpath(config.PATH_WEBRTC, 'src')
    util.cd(webrtc_src_path)

    if sys.platform == 'linux':
        util.exec('bash', 'build/install-build-deps.sh', '--no-prompt')

    if(conf['os'] == 'linux'):
        util.exec('python', 'build/linux/sysroot_scripts/install-sysroot.py', '--arch={}'.format(conf['cpu']))

    args = _generate_args(conf, mode)
    out_path = _generate_out(conf, mode)

    args_file = os.path.join(
        webrtc_src_path, out_path, 'args.gn')

    os.makedirs(util.getpath(webrtc_src_path, out_path), exist_ok=True)

    with open(args_file, 'w') as file:
        file.write('\n'.join(args))

    util.exec('gn', 'gen', out_path)

    util.exec('ninja', '-C', out_path)


def _copy_tree(source_root, source_file, destination):
    file = source_file.replace(source_root, destination)

    os.makedirs(os.path.dirname(file), exist_ok=True)
    shutil.copy(source_file, file)


def dist_headers(conf, clean=True):
    util.cd(config.PATH_ROOT)

    webrtc_src_path = util.getpath(config.PATH_WEBRTC, 'src')
    dist_path = util.getpath(config.DIR_DIST)

    name = _generate_name(conf)

    include_path = os.path.join(dist_path, 'include', 'webrtc')

    if clean:
        shutil.rmtree(include_path, ignore_errors=True)

    os.makedirs(include_path, exist_ok=True)

    for directory in config.API_HEADERS:
        for file_path in glob.iglob(os.path.join(webrtc_src_path, directory, '**', '*.h'), recursive=True):
            _copy_tree(webrtc_src_path, file_path, include_path)

    for directory in config.LEGACY_HEADERS:
        for file_path in glob.iglob(os.path.join(webrtc_src_path, directory, '*.h'), recursive=False):
            _copy_tree(webrtc_src_path, file_path, include_path)

    if not conf['boringssl']:
        for directory in config.SSL_HEADERS:
            for file_path in glob.iglob(os.path.join(webrtc_src_path, directory, '**', '*.h'), recursive=True):
                _copy_tree(webrtc_src_path, file_path, include_path)


def dist_lib(conf, mode, clean=True):
    util.cd(config.PATH_ROOT)

    webrtc_src_path = util.getpath(config.PATH_WEBRTC, 'src')
    dist_path = util.getpath(config.DIR_DIST)

    name = _generate_name(conf)
    out_path = _generate_out(conf, mode)

    lib_path = os.path.join(dist_path, 'lib', mode.lower().capitalize())

    if clean:
        shutil.rmtree(lib_path, ignore_errors=True)

    os.makedirs(lib_path, exist_ok=True)

    for file_path in glob.iglob(os.path.join(webrtc_src_path, out_path, 'obj', '*.lib')):
        shutil.copy(file_path, lib_path)

    for file_path in glob.iglob(os.path.join(webrtc_src_path, out_path, 'obj', '*.a')):
        shutil.copy(file_path, lib_path)


def archive(conf):
    util.cd(config.PATH_ROOT)

    dist_path = util.getpath(config.DIR_DIST)
    name = _generate_name(conf)

    format = 'zip'
    shutil.make_archive(name, format, dist_path)
    # shutil.copy('{}.{}'.format(name, format), dist_path)
    # os.remove('{}.{}'.format(name, format))


if __name__ == '__main__':
    conf = parse_conf(parse_args())

    setup(conf)
    pull(conf)

    # patch(conf)

    dist_headers(conf)

    for mode in conf['mode']:
        build(conf, mode)
        dist_lib(conf, mode)

    if not conf['no_archive']:
        archive(conf)
