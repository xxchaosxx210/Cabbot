import os
import json
import handler
from threading import Lock

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang.builder import Builder
from kivy.graphics import Color
from kivy.graphics import Rectangle

__title__ = "Cabbot"
__version__ = "0.6.9.2"
__author__ = "Paul Millar"
__date__ = "27-12-2020"
__license__ = "GNU Open Source"

# make saving and loading settings from file thread safe
_file_lock = Lock()

Builder.load_string('''
<ImageButton>:
    canvas.before:
        Color:
            rgba: .34, .34, .34, 1
        Rectangle:
            pos: self.pos
            size: self.size
''')


class ImageButton(ButtonBehavior, Image):

    """
    abstract imagebutton uses kivy default color buttons
    """

    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
    
    def on_press(self):
        with self.canvas.before:
            Color(0.19, 0.64, 0.80, 1)
            Rectangle(pos=self.pos, size=self.size)
        return super().on_press()
    
    def on_release(self):
        with self.canvas.before:
            Color(0.34, 0.34, 0.34, 1)
            Rectangle(pos=self.pos, size=self.size)
        return super().on_release()

def load_settings():
    settings = {
                    "debug_ip": "192.168.0.13", 
                    "debug_port": "5000",
                    "android_run_first_time": True, 
                    "audio": True,
                    "auto_bidding": True,
                    "bidding_radius": 0.0,
                    "driver_id": "19152",
                    "host": "http://uk6.coolnagour.com",
                    "satnav": "google",
                    "icabbi_verbose_mode": True
                }
    if os.path.exists("settings.json"):
        _file_lock.acquire()
        with open("settings.json", "r") as fp:
            settings = json.loads(fp.read())
            print("LOADING SETTINGS.JSON FILE")
        _file_lock.release()
    else:
        print("SETTINGS.JSON FILE NOT FOUND LOADING DEFAULT SETTINGS")
    return settings


def save_settings(settings):
    _file_lock.acquire()
    with open("settings.json", "w") as fp:
        fp.write(json.dumps(settings))
        print("SETTINGS SAVED SUCCESSFULLY")
    _file_lock.release()


def dump_to_file(text):
    with open(Globals.DUMP_FILEPATH, "a") as fp:
        fp.write(f"{text} \n")


class Globals:
    # reference to the main app object
    app = None
    # reference to the thread handler
    icabthread = None
    # reference to the main screen object
    mainscrn = None
    # reference to message screen
    message_list_view = None
    # reference to the message dialog
    message_dialog = None
    # reference to the earnings dialog
    earnings_dialog = None
    # maximum size buffer for the main screen output
    TXT_OUTPUT_BUFFER_SIZE = 10000
    # dump file
    DUMP_FILEPATH = "dump.dat"
    # use a global loading dialog. Initialize in main.py
    loading_dialog = None

    settings = {}

    from pydroid import TextSpeak
    from pydroid import play_system_sound as android_play_system_sound
    android_text2speak = TextSpeak()
