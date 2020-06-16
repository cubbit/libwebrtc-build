import os

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
DIR_BUILD = 'build'
DIR_DEPOT_TOOLS = DIR_BUILD + os.path.sep + 'depot_tools'
DIR_WEBRTC = DIR_BUILD + os.path.sep + 'webrtc'
DIR_BORINGSSL = DIR_BUILD + os.path.sep + 'boringssl'

PATH_DEPOT_TOOLS = os.path.join(PATH_ROOT, DIR_DEPOT_TOOLS)
PATH_WEBRTC = os.path.join(PATH_ROOT, DIR_WEBRTC)
PATH_BORINGSSL = os.path.join(PATH_ROOT, DIR_BORINGSSL)

WEBRTC_REVISION = '4147'
WEBRTC_BRANCH = "refs/remotes/branch-heads/{}".format(WEBRTC_REVISION)

cubbit_default = {}
cubbit_default["gn_args"] = [
    'is_component_build=false',
    'rtc_build_opus=false',
    'rtc_enable_protobuf=false',
    'rtc_include_builtin_audio_codecs=false',
    'rtc_include_builtin_video_codecs=false',
    'rtc_include_ilbc=false',
    'rtc_include_internal_audio_device=false',
    'rtc_include_opus=false',
    'rtc_include_pulse_audio=false',
    'rtc_use_dummy_audio_file_devices=true',
    'rtc_use_gtk=false',
    'rtc_use_x11=false',
    'use_custom_libcxx=false',
]
