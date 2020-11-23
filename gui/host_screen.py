from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import sp
from kivy.metrics import dp

from globals import Globals
from globals import save_settings
from globals import handler


class HostScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(HostScreen, self).__init__(**kwargs)
        self.name = "host"

        gdlayout = GridLayout(cols=1, rows=2, spacing=[dp(5)])
        btn_continue = Button(text="Continue", on_release=lambda *args: setattr(Globals.app.root, "current", "status"))
        btn_debug = Button(text="Debug", on_release=self._on_button_debug)
        gdlayout.add_widget(btn_continue)
        gdlayout.add_widget(btn_debug)
        self.add_widget(gdlayout)

        gdlayout.size_hint = (.5, .3)
        gdlayout.pos_hint = {"center_x": .5, "center_y": .5}

    def _on_button_debug(self, *args):
        dlg = DebugDialog()
        dlg.open()


class DebugDialog(Popup):

    def __init__(self, **kwargs):
        super(DebugDialog, self).__init__(**kwargs)
        self.autodismiss = False
        self.title = "Enter IP address and Port"
        self.size_hint = (None, None)
        self.size = (int(Window.width / 1.5), sp(200))

        lbl_ip = Label(text="IP: ", size_hint=(.1, 1))
        self.txt_ip = TextInput(text=Globals.settings["debug_ip"],
                            size_hint=(.9,1), multiline=False)
        lbl_port = Label(text="Port: ", size_hint=(.1, 1))
        self.txt_port = TextInput(text=Globals.settings["debug_port"], size_hint=(.9, 1),
                                multiline=False)
        btn_continue = Button(text="Continue", on_release=self.on_continue)
        btn_continue.size_hint = (1, None)
        btn_continue.height = int(lbl_port.height / 2)

        vbox = BoxLayout(orientation="vertical")
        gdlayout = GridLayout(cols=2, rows=2)
        gdlayout.add_widget(lbl_ip)
        gdlayout.add_widget(self.txt_ip)
        gdlayout.add_widget(lbl_port)
        gdlayout.add_widget(self.txt_port)
        vbox.add_widget(gdlayout)
        vbox.add_widget(btn_continue)
        self.add_widget(vbox)

    def on_continue(self, instance):
        Globals.settings["debug_port"]  = self.txt_port.text
        Globals.settings["debug_ip"] = self.txt_ip.text
        Globals.settings["host"] = "http://{}:{}".format(self.txt_ip.text, self.txt_port.text)
        save_settings(Globals.settings)
        handler.send_message(event=handler.EVENT_HOST_UPDATE, host=Globals.settings["host"])
        Globals.app.root.current = "status"
        self.dismiss()