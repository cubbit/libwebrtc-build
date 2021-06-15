import os

PATH_ROOT = os.path.dirname(os.path.abspath(__file__))

DIR_PATCH = 'patches'
DIR_DIST = 'dist'
DIR_BUILD = 'build'
DIR_DEPOT_TOOLS = DIR_BUILD + os.path.sep + 'depot_tools'
DIR_WEBRTC = DIR_BUILD + os.path.sep + 'webrtc'
DIR_BORINGSSL = DIR_BUILD + os.path.sep + 'boringssl'

PATH_DEPOT_TOOLS = os.path.join(PATH_ROOT, DIR_DEPOT_TOOLS)
PATH_WEBRTC = os.path.join(PATH_ROOT, DIR_WEBRTC)
PATH_BORINGSSL = os.path.join(PATH_ROOT, DIR_BORINGSSL)

# https://chromiumdash.appspot.com/branches
WEBRTC_BRANCH_PREFIX = "refs/remotes/branch-heads/"

API_HEADERS = [
    'api',
    'rtc_base',
    'third_party/abseil-cpp/absl',
]

LEGACY_HEADERS = [
    '.',
    'call',
    'common_audio/include',
    'common_video/generic_frame_descriptor',
    'common_video/include',
    'common_video',
    'logging/rtc_event_log',
    'logging/rtc_event_log/events',
    'media/base',
    'media/engine',
    'modules/audio_coding/include',
    'modules/audio_device/include',
    'modules/async_audio_processing',
    'modules/audio_processing/include',
    'modules/bitrate_controller/include',
    'modules/congestion_controller/include',
    'modules/include',
    'modules/remote_bitrate_estimator/include',
    'modules/rtp_rtcp/include',
    'modules/rtp_rtcp/source',
    'modules/rtp_rtcp/source/rtcp_packet',
    'modules/utility/include',
    'modules/video_coding',
    'modules/video_coding/codecs/h264/include',
    'modules/video_coding/codecs/interface',
    'modules/video_coding/codecs/vp8/include',
    'modules/video_coding/codecs/vp9/include',
    'modules/video_coding/include',
    'p2p/base',
    'pc',
    'system_wrappers/include',
]

SSL_HEADERS = [
    'third_party/boringssl/src/include',
]

cubbit_default = {}
cubbit_default["gn_args"] = [
    'is_component_build=false',
    'rtc_build_examples=false',
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

    'rtc_include_tests=false',
    'rtc_disable_metrics=false',
    'rtc_build_tools=false',
    # 'rtc_exclude_transient_suppressor=true',
    'rtc_disable_trace_events=true',
]

webrtc_patches = {}
webrtc_patches["linux_x64"] = [
    'linux_libcxx.patch'
]
