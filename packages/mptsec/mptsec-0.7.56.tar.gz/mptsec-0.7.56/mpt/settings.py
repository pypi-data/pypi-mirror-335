from os.path import expanduser
import os
import datetime

import mpt.config
from mpt.config import Config

__version__ = '0.7.56'
HOME_FOLDER = expanduser("~")
DEFAULT_MOBILE_FOLDER = os.path.join(HOME_FOLDER, "tools/MOBILE/")
MPT_BIN = os.path.join(DEFAULT_MOBILE_FOLDER, 'bin')
MPT_PATH = os.path.dirname(os.path.realpath(__file__))
PENTEST_FOLDER = 'pentest-' + datetime.datetime.today().strftime('%Y-%m-%d') # pentest-YYYY-MM-DD
APP_FOLDER = "app"
BACKUP_FOLDER = "backup"
SCREENSHOT_FOLDER = "screenshots"
SOURCE_FOLDER = "source"
BURP_FOLDER = "burp"
FRIDA_BIN = "frida-server"
TEMP_DIR = "/tmp/local-mpt/"
BROWSER = 'chromium'
DECOMPILER='jadx' # jd-gui, luyten
DEFAULT_TERMINAL='gnome-terminal'
conf = Config()
# Default installation for is set in Config() use conf.load_config('install-dir')

# note
# sh does not support source command and it was replaces with .
# "The . is POSIX-compliant and also works in /bin/sh."

ANDROID_TOOLS = {
    # available parameters
    # bin
    #   - variable BIN should be absolute path in format <folder>/<path-to/bin>
    # dir
    #   - use DIR variable if after download the tool extracts the binary subdirectory like folder/folder/bin
    #     required if BIN starts with command instead of /
    #     will be created before download starts
    # pre
    #   - pre install instructions
    # post
    #  - post install instructions
    # bin_info
    #  - log.info(<bin_log>) before executing command
    # download_dir
    #  - define directory to download and decompress files
    # requirement_checks
    #  - define dependency-checks for the application, the check should return true or false, multiple checks are split by semicolon
    #    e.g. python -m poetry -V    will check if poetry is installed
    #    which git will check if poetry is installed
    # bin_global
    #  - takes a python dictionary for setting symbolic links after installation to link them to MPT_BIN
    #  - {link_name: 'location/to/bin/from/dir' }  the path should be relative to package {dir} folder


    # template
    #'jadx': {
    #   'url': 'https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip',
    #   'info': '',
    #   'bin': os.path.join(MOBILE_FOLDER, 'jadx/bin/jadx-gui'),
    #   'bin_info': 'Open MobSF in browser: http://127.0.0.1:8000\n Use ctrl+C to close application',
    #   'dir': 'jadx',
    #   'download_dir': 'jadx'
    #   'install': 'http',
    #   'pre': 'mkdir jadx'
    #   'post': 'mv jadx-1.4.7 jadx'
    #   'requirement_checks': 'which hostapd; which dnsmasq'
    #   'bin_global': {'jadx': 'bin/jadx', 'jadx-gui': 'bin/jadx-gui'}
    #},

    'MobSF': {
        # check updates: 'https://github.com/MobSF/Mobile-Security-Framework-MobSF'
        # fix dependency in mobSF (remove if not required) ->  sed -i \'s/packaging = ">=21\.3,<22\.0"/packaging = ">=24\.2"/\' pyproject.toml
        'url': 'https://github.com/MobSF/Mobile-Security-Framework-MobSF/archive/refs/tags/v4.3.0.zip',
        'info': 'Mobile Security Framework (MobSF)',
        'bin': 'cd {}; python -m venv venv; . ./venv/bin/activate; . ./run.sh'.format(os.path.join(conf.load_config('install-dir'), 'MobSF')),
        'bin_info': 'Open MobSF in browser: http://127.0.0.1:8000 (Press CTRL+C to quit)',
        'dir': 'MobSF',
        'install': 'http',
        'post': 'mv Mobile-Security-Framework-MobSF-4.3.0 MobSF; cd MobSF; python -m venv venv; . ./venv/bin/activate; pip install poetry; . ./setup.sh',
    },

    # RMS installation old version
    # 'RMS': {
    #    'url': 'https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security',
    #    'info': 'Runtime Mobile Security (RMS)',
    #    'dir': 'RMS',
    #    'bin': 'node ' + os.path.join(conf.load_config('install-dir') + 'RMS/rms.js'),
    #    'bin_info': 'Running on http://127.0.0.1:5491/ (Press CTRL+C to quit)',
    #    'install': 'git',
    #    'post': 'mv RMS-Runtime-Mobile-Security RMS; cd RMS; npm install; npm run compile',
    #    'requirement_checks': 'npm -v'
    #},

    'RMS': {
        # check 'https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security',
        #
        # HOW TO SELECT A RIGHT NODEJS VERSION ??
        #   https://github.com/ChiChou/Grapefruit/wiki/How-do-I-decide-which-version-of-nodejs-to-use%3F
        #
        #   You need to find the right node version. To check which nodejs is supported, you can refer to these two pages:
        #       Releases frida -> https://github.com/frida/frida/releases
        #       Previous Releases Node.js -> https://nodejs.org/en/about/previous-releases
        #   example:
        #       last available frida node version for linux: frida-v16.5.9-node-v127-linux-x64.tar.gz   ==> v127
        #       Based on release node page: Module Version v127 ==> Node.js Version => v22.12.0
        #       we need to install v22.12.0
        #       put the correct version in post command "... nodeenv --python-virtualenv --node 22.12.0 ..."
        #
        'info': 'Runtime Mobile Security (RMS)',
        'dir': 'RMS',
        'bin': 'cd {}; . ./venv/bin/activate; rms'.format(os.path.join(conf.load_config('install-dir'), 'RMS')),
        'bin_info': 'Running on http://127.0.0.1:5491/ (Press CTRL+C to quit)',
        'install': 'local',
        # install nodejs locally within the python virtual environment
        'post': 'cd RMS; python -m venv venv; . ./venv/bin/activate; pip install nodeenv; nodeenv --python-virtualenv --node 22.12.0; npm install -g rms-runtime-mobile-security',
    },
    'objection': {
        # check: 'https://github.com/sensepost/objection',
        'info': 'Runtime Mobile Exploration Toolkit',
        'dir': 'objection',
        # 'bin_info': 'Please run "frida-ps -U" to find an app and start objection with the following command:\nobjection --gadget "<APP-NAME>" explore',
        'bin': 'cd {}; . ./venv/bin/activate; objection'.format(os.path.join(conf.load_config('install-dir'), 'objection')),
        'install': 'local',
        # 'post': 'cd objection; python -m venv venv; source ./venv/bin/activate; pip install --upgrade setuptools; pip install -U objection'
        'post': 'cd objection; python -m venv venv; . ./venv/bin/activate; pip install --upgrade setuptools; pip install -U objection'
    },
    'spotbugs': {
        # check: 'https://github.com/spotbugs/spotbugs/releases',
        'url': 'https://github.com/spotbugs/spotbugs/releases/download/4.9.3/spotbugs-4.9.3.zip',
        'info': 'Static code analysis for vulnerabilities and bugs',
        'dir': 'spotbugs',
        'bin': f'cd {os.path.join(conf.load_config('install-dir'), 'spotbugs')}; ./bin/spotbugs',
        'install': 'http',
        'post': 'mv spotbugs-4.9.3 spotbugs',
        'bin_global': {'spotbugs': 'bin/spotbugs'}
    },
    'jadx': {
        # check updates: 'https://github.com/skylot/jadx/releases'
        'url': 'https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip',
        'info': 'Dex to Java decompiler',
        'bin': os.path.join(conf.load_config('install-dir'), 'jadx/bin/jadx-gui'),
        'dir': 'jadx',
        'download_dir': 'jadx',
        'install': 'http',
        'pre': 'mkdir jadx',
        'bin_global': {'jadx': 'bin/jadx', 'jadx-gui': 'bin/jadx-gui'}
    },
    'jd-gui': {
        # check updates: 'https://github.com/java-decompiler/jd-gui/releases'
        'url': 'https://github.com/java-decompiler/jd-gui/releases/download/v1.6.6/jd-gui-1.6.6.jar',
        'info': 'Java Decompiler, dex2jar required',
        'bin': os.path.join(conf.load_config('install-dir'), 'jd-gui/jd-gui.jar'),
        'dir': 'jd-gui',
        'install': 'http',
    },
    'luyten': {
        # check updates https://github.com/deathmarine/Luyten/releases
        'url': 'https://github.com/deathmarine/Luyten/releases/download/v0.5.4_Rebuilt_with_Latest_depenencies/luyten-0.5.4.jar',
        'info': 'Java Decompiler Gui for Procyon',
        'bin': os.path.join(conf.load_config('install-dir'), 'luyten/luyten.jar'),
        'dir': 'luyten',
        'install': 'http'
    },
    'sqlitestudio': {
        # check updates : https://github.com/pawelsalawa/sqlitestudio/releases
        'url': 'https://github.com/pawelsalawa/sqlitestudio/releases/download/3.4.17/sqlitestudio-3.4.17-linux-x64.tar.xz',
        'info': 'Multi-platform SQLite database manager',
        'dir': 'SQLiteStudio',
        'bin': os.path.join(conf.load_config('install-dir'), 'SQLiteStudio/sqlitestudio'),
        'install': 'http',
        'bin_global': {'sqlitestudio': 'sqlitestudio', 'sqlitestudiocli': 'sqlitestudiocli'}
    },
    'pidcat': {
        'url': 'https://github.com/JakeWharton/pidcat',
        'info': 'excellent logcat color script',
        'bin': os.path.join(conf.load_config('install-dir') + 'pidcat/pidcat.py'),
        'dir': 'pidcat',
        'install': 'git'
    },
    'pidcat-ex': {
        'url': 'https://github.com/healthluck/pidcat-ex.git',
        'info': 'PID Cat (extended version)',
        'bin': os.path.join(conf.load_config('install-dir') + 'pidcat-ex/pidcat-ex.py'),
        'dir': 'pidcat-ex',
        'install': 'git'
    },
    'adus': {
        'url': 'https://github.com/ByteSnipers/adus',
        'info': 'Bash script to dump, build and sign apk',
        'bin': os.path.join(conf.load_config('install-dir') + 'adus/adus.sh'),
        'dir': 'adus',
        'install': 'git'
    },
    'fridump': {
        # check https://github.com/rootbsd/fridump3 (updated version)
        # https://github.com/Nightbringer21/fridump (obsolete version)
        'url': 'https://github.com/rootbsd/fridump3',
        'info': 'Memory dumping tool using frida',
        'bin': f'cd {os.path.join(conf.load_config('install-dir'),'fridump')}; . ./venv/bin/activate; python fridump3.py',
        'dir': 'fridump',
        'install': 'git',
        'post': 'cd fridump; python -m venv venv; . ./venv/bin/activate; pip install --upgrade frida-tools; chmod +x fridump3.py'
    },
    'adb': {
        'url': 'https://dl.google.com/android/repository/platform-tools-latest-linux.zip',
        'info': 'Android Debug Bridge (adb)',
        'dir': 'platform-tools',
        'bin': os.path.join(conf.load_config('install-dir'), 'platform-tools/adb'),
        'install': 'http',
        'bin_global': {'adb': 'adb', 'fastboot': 'fastboot', 'sqlite3': 'sqlite3'}
    },
    'aapt': {
        # check version and replace r34 with the latest one: https://developer.android.com/tools/releases/build-tools
        # URL examples
        #  version + RC: https://dl.google.com/android/repository/build-tools_r34-rc3-linux.zip'
        #  version:      https://dl.google.com/android/repository/build-tools_r34-linux.zip  # android 14
        'url': 'https://dl.google.com/android/repository/build-tools_r34-rc3-linux.zip', # android 14
        'info': 'Android Asset Packaging Tool',
        'bin': os.path.join(conf.load_config('install-dir'), 'build-tools/aapt'),
        'dir': 'build-tools',
        'install': 'http',
        'post': 'mv android-UpsideDownCake build-tools',
        # 'post': 'mv android-14 build-tools',
        #' cp -r android-14/lib64 build-tools/lib; cp -r android-14/lib64 build-tools/lib; cp android-14/aapt build-tools/aapt; cp android-14/aapt2 build-tools/aapt2; cp android-14/apksigner build-tools/apksigner ;rm -rf android-14',
        'bin_global': {'aapt': 'aapt', 'aapt2': 'aapt2', 'apksigner': 'apksigner', 'dexdump': 'dexdump', 'split-select': 'split-select', 'zipalign': 'zipalign'}
    },
    'abe': {
        # check updates: https://github.com/nelenkov/android-backup-extractor/releases
        'url': 'https://github.com/nelenkov/android-backup-extractor/releases/download/latest/abe-0059753.jar', # 2024-11
        'info': 'Android backup extractor, android:allowBackup="true" required',
        'bin': os.path.join(conf.load_config('install-dir'), 'abe/abe.jar'),
        'dir': 'abe',
        'install': 'http'
    },
    'signapk': {
        'url': 'https://github.com/appium-boneyard/sign',
        'info': 'sign an apk with the Android test certificate',
        'bin': os.path.join(conf.load_config('install-dir'),'sign/dist/signapk.jar'), # not tested
        'dir': 'sign',
        'install': 'git'
    },
    'apktool': {
        # check https://bitbucket.org/iBotPeaches/apktool/downloads/ and https://apktool.org/blog
        'url': 'https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.11.1.jar',
        'info': 'A tool for reverse engineering Android apk files',
        'bin': os.path.join(conf.load_config('install-dir'), 'apktool/apktool.jar'),
        'dir': 'apktool',
        'install': 'http'
    },
    'dex2jar': {
        # check https://github.com/pxb1988/dex2jar/
        'url': 'https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex-tools-v2.4.zip',
        'info': 'Convert the Dalvik Executable (.dex) file to jar',
        'bin': os.path.join(conf.load_config('install-dir'), 'dex2jar/d2j-dex2jar.sh'),
        'dir': 'dex2jar',
        'install': 'http',
        'post': 'mv dex-tools-v2.4 dex2jar',
        'bin_global': {
            'd2j-apk-sign.sh': 'd2j-apk-sign.sh', 'd2j-asm-verify.sh': 'd2j-asm-verify.sh', 'd2j-baksmali.sh': 'd2j-baksmali.sh',
            'd2j-class-version-switch.sh': 'd2j-class-version-switch.sh', 'd2j-decrypt-string.sh': 'd2j-decrypt-string.sh', 'd2j-dex2jar.sh': 'd2j-dex2jar.sh',
            'd2j-dex2smali.sh': 'd2j-dex2smali.sh', 'd2j-dex-recompute-checksum.sh': 'd2j-dex-recompute-checksum.sh', 'd2j-dex-weaver.sh': 'd2j-dex-weaver.sh',
            'd2j_invoke.sh': 'd2j_invoke.sh', 'd2j-jar2dex.sh': 'd2j-jar2dex.sh', 'd2j-jar2jasmin.sh': 'd2j-jar2jasmin.sh',
            'd2j-jar-access.sh': 'd2j-jar-access.sh', 'd2j-jar-weaver.sh': 'd2j-jar-weaver.sh', 'd2j-jasmin2jar.sh': 'd2j-jasmin2jar.sh',
            'd2j-smali.sh': 'd2j-smali.sh','d2j-std-apk.sh': 'd2j-std-apk.sh'
        }
    },
    'janus': {
        'url': 'https://github.com/ppapadatis/python-janus-vulnerability-scan',
        'info': 'scans an APK and an Android device for CVE-2017–13156',
        'bin': 'cd {}; . ./venv/bin/activate; python janus.py'.format(os.path.join(conf.load_config('install-dir'), 'python-janus-vulnerability-scan')),
        'dir': 'python-janus-vulnerability-scan',
        'install': 'git',
        'post': 'cd python-janus-vulnerability-scan; python -m venv venv; . ./venv/bin/activate; pip install -r requirements.txt'
    },
    'linux-router': {
        'url': 'https://github.com/garywill/linux-router',
        'info': 'Set Linux as router in one command. Able to provide Internet, or create WiFi hotspot',
        'bin': 'cd {}; sudo ./lnxrouter'.format(os.path.join(conf.load_config('install-dir'), 'linux-router')),
        'dir': 'linux-router',
        'install': 'git',
        'requirement_checks': 'which hostapd; which dnsmasq'
    },
    'kitty': {
        # check https://sw.kovidgoyal.net/kitty/binary/
        # requirement tool to objection execution with interactive cli
        'info': 'The fast, feature-rich, GPU based terminal emulator',
        'bin': os.path.join(conf.load_config('install-dir'), 'kitty/kitty.app/bin/kitty'),
        'dir': 'kitty',
        'install': 'local',
        'post': 'curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin dest={} launch=n'.format(os.path.join(conf.load_config('install-dir'),'kitty'))
    },
    'scrcpy': {
        # check version and replace file: https://github.com/Genymobile/scrcpy/releases
        'url': 'https://github.com/Genymobile/scrcpy/releases/download/v3.1/scrcpy-linux-x86_64-v3.1.tar.gz',
        'info': 'Application mirrors Android devices (video and audio) connected via USB',
        'bin': os.path.join(conf.load_config('install-dir'), 'scrcpy/scrcpy'),
        'dir': 'scrcpy',
        'install': 'http',
        'post': 'mv scrcpy-linux-x86_64-v3.1 scrcpy'
    }
}

ANDROID_APKS = {
    'Xposed':{
       'url': 'https://forum.xda-developers.com/attachment.php?attachmentid=4393082&d=1516301692', # link with redirect
            # https://repo.xposed.info/module/de.robv.android.xposed.installer
            # https://forum.xda-developers.com/showthread.php?t=3034811
        'apk': 'apps/XposedInstaller_3.1.5.apk',
        'pkg': 'de.robv.android.xposed.installer'
    },

    'JustTrustMe': {
        'url' :'https://github.com/Fuzion24/JustTrustMe',
        'apk': 'apps/JustTrustMe-singed.apk',
        'pkg': 'just.trust.me'

        # latest version is not available in releases https://github.com/Fuzion24/JustTrustMe/releases
        # compiled latest version with gradlew
        # git clone https://github.com/Fuzion24/JustTrustMe.git
        # export ANDROID_HOME=~/Android/Sdk; cd JustTrustMe; ./gradlew assembleRelease
    },

    'Drozer Agent': {
        'url': 'https://github.com/mwrlabs/drozer/releases/download/2.3.4/drozer-agent-2.3.4.apk',
        'apk': 'apps/drozer-agent-2.3.4.apk',
        'pkg': 'com.mwr.dz'
    },

    'Inspeckage': {
        'url': 'https://github.com/ac-pm/Inspeckage/releases/download/v2.4/app-release.apk',
        'apk': 'apps/inspackage-v2.4.apk',
        'pkg': 'mobi.acpm.inspeckage'
    },

    'RootCloak': {
        'url': 'https://github.com/devadvance/rootcloak/releases/download/v3.0-beta_20160731_2/app-release.apk',
        'apk': 'apps/RootCloak-v3.0beta.apk',
        'pkg': 'com.devadvance.rootcloak2'
    }
    #'droidmon': 'https://github.com/idanr1986/droidmon',
}
