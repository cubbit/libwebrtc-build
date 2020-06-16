import argparse
import os

import config
import util


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--boringssl', type=str, action='store')
    parser.add_argument('--cpu', type=str, action='store', required=True)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--no-cubbit', action='store_true')
    parser.add_argument('--no-log', action='store_true')
    parser.add_argument('--os', type=str, action='store', required=True)
    parser.add_argument('--rtti', action='store_true')

    return parser.parse_args()


def parse_conf(args):
    conf = {}

    conf['boringssl'] = str(args.boringssl)
    conf['cpu'] = str(args.cpu)
    conf['cubbit'] = not bool(args.no_cubbit)
    conf['debug'] = bool(args.debug)
    conf['no_log'] = bool(args.no_log)
    conf['os'] = str(args.os)
    conf['rtti'] = bool(args.rtti)

    return conf


def setup(conf):
    if os.path.exists(util.getpath(config.PATH_DEPOT_TOOLS)):
        util.cd(config.PATH_DEPOT_TOOLS)
        util.exec('git', 'checkout', '-f', 'master')
        util.exec('git', 'pull')
    else:
        util.exec('git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git',
                  util.getpath(config.PATH_DEPOT_TOOLS))

    os.environ['PATH'] = util.getpath(
        config.PATH_DEPOT_TOOLS) + os.path.pathsep + os.environ['PATH']

    if(os.name == 'nt'):
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
            conf['boringssl_path'] = util.getpath(config.PATH_BORINGSSL, 'src', 'include')
        elif os.path.exists(util.getpath(config.PATH_BORINGSSL, 'src')):
            conf['boringssl_path'] = util.getpath(config.PATH_BORINGSSL, 'src')
        else:
            conf['boringssl_path'] = util.getpath(config.PATH_BORINGSSL)

def pull(conf):
    webrtc_path = util.getpath(config.PATH_WEBRTC)

    util.cd(webrtc_path)
    if not util.exists(webrtc_path, '.gclient'):
        util.exec('fetch', '--nohooks', 'webrtc')

    util.cd(webrtc_path, 'src')

    util.exec('git', 'reset', '--hard')
    util.exec('git', 'fetch', 'origin')
    util.exec('git', 'checkout', config.WEBRTC_BRANCH)

    util.exec('gclient', 'sync', '-D')


def patch(conf):
    webrtc_src_path = util.getpath(config.PATH_WEBRTC, 'src')

    if conf['no_log']:
        log_file = os.path.join(
            webrtc_src_path, 'rtc_base{}logging.cc'.format(os.path.sep))
        with open(log_file, 'r') as file:
            filedata = file.read()
        filedata = filedata.replace(
            'LoggingSeverity g_min_sev = LS_INFO', 'LoggingSeverity g_min_sev = LS_NONE')
        filedata = filedata.replace(
            'LoggingSeverity g_dbg_sev = LS_INFO', 'LoggingSeverity g_dbg_sev = LS_NONE')
        with open(log_file, 'w') as file:
            file.write(filedata)


def _generate_args(conf):
    args = []

    args.append('target_os="{}"'.format(conf['os']))
    args.append('target_cpu="{}"'.format(conf['cpu']))

    if conf['cubbit']:
        args = args + config.cubbit_default['gn_args']

    if conf['debug']:
        args.append('is_debug=true')
    else:
        args.append('is_debug=false')

    if conf['rtti']:
        args.append('use_rtti=true')
    else:
        args.append('use_rtti=false')

    if conf['boringssl']:
        args.append('rtc_build_ssl=false')
        args.append('rtc_ssl_root="{}"'.format(conf['boringssl_path']))
    else:
        args.append('rtc_build_ssl=true')

    return args


def _generate_name(conf):
    separator = '-'
    name = 'webrtc'

    name = separator.join([name, config.WEBRTC_REVISION])

    name = separator.join([name, conf['os']])
    name = separator.join([name, conf['cpu']])

    if conf['cubbit']:
        name = separator.join([name, 'cubbit'])

    if conf['rtti']:
        name = separator.join([name, 'rtti'])

    if conf['boringssl']:
        name = separator.join([name, 'boringssl_{}'.format(conf['boringssl'][:8])])

    if conf['no_log']:
        name = separator.join([name, 'nolog'])

    if conf['debug']:
        name = separator.join([name, 'debug'])
    else:
        name = separator.join([name, 'release'])

    return name


def build(conf):
    webrtc_src_path = util.getpath(config.PATH_WEBRTC, 'src')
    util.cd(webrtc_src_path)

    name = _generate_name(conf)
    args = _generate_args(conf)

    print(name)

    out_path = 'out/{}'.format(name)

    args_file = os.path.join(
        webrtc_src_path, out_path, 'args.gn')

    util.exec('gn', 'gen', out_path)

    with open(args_file, 'w') as file:
        file.write('\n'.join(args))

    util.exec('gn', 'gen', out_path)

    # for build_target in conf['build_targets']:
    # util.exec('ninja', '-C', out_path, build_target)
    util.exec('ninja', '-C', out_path, 'webrtc')


if __name__ == '__main__':
    args = parse_args()
    conf = parse_conf(args)

    setup(conf)
    # pull(conf)
    # patch(conf)
    build(conf)