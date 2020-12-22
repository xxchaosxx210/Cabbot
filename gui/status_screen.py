from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label

from dialogs import show_toast
from dialogs import EarningsDialog
from dialogs import BusyDialog
from dialogs import InfoDialog
from dialogs import MessageDialog

from gui.settings_screen import _is_debug_host

from globals import handler
from globals import Globals
from globals import save_settings
from globals import ImageButton

import json

from pydroid import navigate_google_maps
from pydroid import navigate_waze
from pydroid import phone_call


Builder.load_string('''
<StatusScreen>:
    name: "status"
    BoxLayout:
        orientation:"vertical"
        GridLayout:
            size_hint: 1, .1
            cols: 2
            rows: 1
            Label:
                markup: True
                text: ""
                id: id_run_mode_label
            Label:
                text: "Connecting..."
                id: id_status_label
        BoxLayout:
            orientation: "horizontal"
            size_hint: 1, .1
            Button:
                text: "Earnings"
                on_release: root.on_earning_button(self)
            Button:
                text: "Extra"
                on_release: root.on_extras_button(self)
            ImageButton:
                source: "./res/settings.png"
                on_release: root.on_settings_button(self)
                size_hint: .3, 1
        BoxLayout:
            orientation: "vertical"
            padding: 
            NameValueScroll:
                size_hint: 1, .3
                id: sv_namevalue
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    Label:
                        text: sv_namevalue.nametext
                        markup: True
                        size_hint_x: .2
                        text_size: self.width, None
                        height: self.texture_size[1]
                        size_hint_y: None
                        font_size: "16sp"
                    ValueStatusLabel:
                        size_hint_x: .8
                        markup: True
                        text: sv_namevalue.valuetext
                        text_size: self.width, None
                        height: self.texture_size[1]
                        size_hint_y: None
                        font_size: "16sp"
            HeaderViewContainer:
                size_hint: 1, .5
                id: headerview_id
        BoxLayout:
            size_hint: 1, .1
            orientation: "horizontal"
            Button:
                text: "Start"
                on_release: root.on_start_button(self)
                background_normal: ''
                background_color: .1, .7, .1, 1
            BoxLayout:
                orientation: "horizontal"
                ToggleButton:
                    text: "Auto Bid"
                    state: "normal"
                    on_release: root.on_autobid_button(self)
                    id: auto_bid_button
            Button:
                background_normal: ''
                background_color: .7, .1, .1, 1
                text: "Busy"
                on_release: root.on_busy_button(self)
''')

class NameValueScroll(ScrollView):

    nametext = StringProperty("")
    valuetext = StringProperty("")

    def add(self, name, value):
        self.nametext += f" \n{name}"
        self.valuetext += f" \n{value}"
    
    def clear(self):
        self.scroll_y = 1
        self.nametext = ""
        self.valuetext = ""


class StatusScreen(Screen):
    name_text = StringProperty("")
    value_text = StringProperty("")
    prebooking_text = StringProperty("")
    status_text = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(StatusScreen, self).__init__(*args, **kwargs)
    
    def on_settings_button(self, button):
        Globals.app.root.current = "settings"

    def on_autobid_button(self, button):
        if button.state == "normal":
            active = False
        else:
            active = True
        handler.send_message(event=handler.EVENT_CHANGE_BIDDING, enable=active)

    def on_enter(self, *args):
        Globals.mainscrn = self
        self.set_running_mode_label()
        if Globals.settings["auto_bidding"]:
            self.ids["auto_bid_button"].state = "down"
        else:
            self.ids["auto_bid_button"].state = "normal"
        handler.send_message(event=handler.EVENT_ANDROID_START_GPS)

    def set_running_mode_label(self):
        if _is_debug_host.search(Globals.settings["host"]):
            self.ids["id_run_mode_label"].text = "[color=#ff0000]Debug Mode[/color]"
        else:
            self.ids["id_run_mode_label"].text = "[color=#00ff11]Live Mode[/color]"
    
    def on_start_button(self, start_button):
        handler.send_message(event=handler.EVENT_CHECK_STATUS)
        if not Globals.icabthread.isAlive():
            dlg = MessageDialog()
            dlg.message_label.text = "Bot Thread is dead something went wrong!!"
            dlg.open()
        if start_button.text == "Start":
            show_toast("Scanning Started", 2)
            start_button.text = "Stop"
        else:
            show_toast("Scanning Stopped", 2)
            start_button.text = "Start"
    
    def on_busy_button(self, button):
        dlg = BusyDialog()
        dlg.open()
    
    def on_earning_button(self, button):
        dlg = EarningsDialog()
        dlg.open()
    
    def on_extras_button(self, button):
        Globals.app.root.current = "extras"
    

class ValueStatusLabel(Label):
    """handles the markup link press events in the mainscrn"""
    def on_ref_press(self, ref):
        ref = json.loads(ref)
        print(ref)
        if "action" in ref:
            handler.send_message(event=handler.EVENT_BOOKING_UPDATE, 
                                booking_id=ref["booking_id"], 
                                status=ref["action"])
        elif "phone" in ref:
            dlg = InfoDialog()
            dlg.set_phone_and_name(ref["name"], ref["phone"])
            dlg.open()
        elif "address" in ref:
            if Globals.settings["satnav"] == "google":
                navigate_google_maps("geo:0,0?q={},{}".format(ref["lat"], ref["lng"]))
            else:
                navigate_waze(ref["lat"], ref["lng"])
        elif "destination" in ref:
            Globals.android_text2speak.speak("Setting destination for {}".format(ref["username"]))
            if Globals.settings["satnav"] == "google":
                navigate_google_maps("geo:0,0?q={},{}".format(ref["lat"], ref["lng"]))
            else:
                navigate_waze(ref["lat"], ref["lng"])
        elif "direct" in ref:
            phone_call(ref["direct"])



