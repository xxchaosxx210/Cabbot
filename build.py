from subprocess import PIPE, Popen
import sys
import os
from globals import __version__

def communicate_process(args):
    _process = Popen(args, stdout=PIPE)
    _stdout = _process.communicate()
    return _stdout[0].decode("utf-8")

os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
print(communicate_process(["buildozer", "-v", "android", "debug"]))
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":
        print("Debugging Android APK. Please make sure device is connected.")
        print(communicate_process(["adb", "uninstall", "org.cabbot.cabbot"]))
        print(communicate_process(["adb", "install", f"./bin/cabbot-{__version__}-debug.apk"]))
        print(communicate_process(["adb", "shell", "monkey", "-p", "org.cabbot.cabbot", "-c", "android.intent.category.LAUNCHER", "1"]))
        print(communicate_process(["adb", "logcat", "-c"]))
        print(communicate_process(["clear"]))
        os.system("adb logcat \"python:I\" \"*:S\"")
        #print(communicate_process(["adb", "logcat", "\"python:I\"", "\"*:S\""]))
        #adb shell monkey -p org.cabbot.cabbot -c android.intent.category.LAUNCHER 1
