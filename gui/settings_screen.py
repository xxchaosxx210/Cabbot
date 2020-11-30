from kivy.uix.screenmanager import Screen
from kivy.uix.switch import Switch
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.lang.builder import Builder
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.metrics import dp as kivydp

from globals import Globals
from globals import save_settings
from globals import handler

import re

_is_debug_host = re.compile(r'^http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,6}$')

Builder.load_string('''
<BiddingRangeWidget>:
    canvas.before:
        Color:
            rgba: .6, .6, .6, 1
        Line:
            width: 2
            rectangle: self.x, self.y, self.width, self.height
''')


class BiddingRangeWidget(GridLayout):

    """ contains the bid range slider and label """

    def __init__(self, **kwargs):
        super(BiddingRangeWidget, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2
        self.label = Label(text="Bid Range (Miles): 0.0")
        self.slider = Slider(min=0.0, max=15.0, step=0.1)
        self.add_widget(self.label)
        self.add_widget(self.slider)
        self.slider.bind(value=self.on_value)
    
    def on_value(self, *args):
        self.label.text = "Bid Range (Miles): {:.2f}".format(self.slider.value)


class DebugWidget(GridLayout):

    """ Contains the debug ip and port textinputs """

    def __init__(self, **kwargs):
        super(DebugWidget, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        lbl_ip = Label(text="IP: ")
        lbl_port = Label(text="Port: ")
        self.txt_ip = TextInput(text="")
        self.txt_port = TextInput(text="")
        self.add_widget(lbl_ip)
        self.add_widget(self.txt_ip)
        self.add_widget(lbl_port)
        self.add_widget(self.txt_port)
    
    def set_ip_and_port(self, ip, port):
        self.txt_ip.text = ip
        self.txt_port.text = port
    
    def get_ip_and_port(self):
        return (self.txt_ip.text, self.txt_port.text)
    
    def disable_widgets(self, disabled):
        self.txt_ip.disabled = disabled
        self.txt_port.disabled = disabled


class DriverWidget(GridLayout):

    """ Container for holding the Driver ID and Host dropdown"""

    def __init__(self, **kwargs):
        self.cols = 2
        self.rows = 2
        super(DriverWidget, self).__init__(**kwargs)
        label = Label(text="Driver ID: ", size_hint=(.1, 1))
        self.txt_driverid = TextInput(text="", size_hint=(.4, 1))
        self.txt_driverid.bind(text=check_value_isdigit)
        
        self.btn_host = Button(text="Select Host")
        self.btn_host.bind(on_release=self.show_dropdown)
        lbl_host = Label(text="Host: ")

        self.add_widget(label)
        self.add_widget(self.txt_driverid)
        self.add_widget(lbl_host)
        self.add_widget(self.btn_host)
        
        self.host = ""

    def show_dropdown(self, button, *args):
        """ Display the Dropdown widget with the Host Name buttons """
        _dp = DropDown()
        _dp.bind(on_select=lambda instance, _item: setattr(button, 'text', _item.text))
        for host in ["ABC", "GOLDSTAR", "DEBUG"]:
            item = Button(text=host, size_hint_y=None, height=kivydp(44))
            item.bind(on_release=lambda btn: _dp.select(btn))
            _dp.add_widget(item)
        _dp.bind(on_select=self._on_host_selection)
        _dp.open(button)
    
    def _on_host_selection(self, _dd_, _btn_):
        """ set the host and disable or enable debug ip and port textinput widgets """
        if _btn_.text == "ABC":
            self.host = "http://uk6.coolnagour.com"
            SettingsScreen.instance.debugbox.disable_widgets(True)
            SettingsScreen.instance.debug_mode = False
        elif _btn_.text == "GOLDSTAR":
            self.host = "http://uk7.coolnagour.com"
            SettingsScreen.instance.debugbox.disable_widgets(True)
            SettingsScreen.instance.debug_mode = False
        elif _btn_.text == "DEBUG":
            ip, port = SettingsScreen.instance.debugbox.get_ip_and_port()
            SettingsScreen.instance.debugbox.disable_widgets(False)
            SettingsScreen.instance.debug_mode = True
            self.host = f"http://{ip}:{port}"
        else:
            self.host = ""
    
    def set_driver_id(self, drvid):
        self.txt_driverid.text = drvid
    
    def set_host(self, host):
        """
        store the host variable, set the button text according with the host url. 
        Also disable the debug textinputs if debug not selected.

        ABC      - http://uk6.
        GOLDSTAR - http://uk7. etc.."""

        self.host = host
        debug_mode = False
        if host == "http://uk6.coolnagour.com":
            self.btn_host.text = "ABC"
            SettingsScreen.instance.debugbox.disable_widgets(True)
        elif host == "http://uk7.coolnagour.com":
            self.btn_host.text = "GOLDSTAR"
            SettingsScreen.instance.debugbox.disable_widgets(True)
        elif _is_debug_host.search(host):
            self.btn_host.text = "DEBUG"
            SettingsScreen.instance.debugbox.disable_widgets(False)
            debug_mode = True
        else:
            self.btn_host.text = "Select Host"
            self.host = ""
        return debug_mode

class SwitchButton(GridLayout):

    """ Container for holding a switch button """

    def __init__(self, label="", **kwargs):
        super(SwitchButton, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 1
        self.label = Label(text=label)
        self.switch = Switch(active=True)
        self.add_widget(self.label)
        self.add_widget(self.switch)


class SatNavWidget(GridLayout):

    def __init__(self, **kwargs):
        super(SatNavWidget, self).__init__(**kwargs)
        self.rows = 1
        self.cols = 2
        lbl_satnav = Label(text="Launch Navigation: ")
        self.btn_satnav = Button(text="Google")
        self.btn_satnav.bind(on_release=self.show_dropdown)
        self.add_widget(lbl_satnav)
        self.add_widget(self.btn_satnav)
    
    def show_dropdown(self, button, *args):
        """ Display the Dropdown widget with the Host Name buttons """
        _dp = DropDown()
        _dp.bind(on_select=lambda instance, _item: setattr(button, 'text', _item.text))
        for host in ["Google", "Waze"]:
            item = Button(text=host, size_hint_y=None, height=kivydp(44))
            item.bind(on_release=lambda btn: _dp.select(btn))
            _dp.add_widget(item)
        #_dp.bind(on_select=self._on_host_selection)
        _dp.open(button)


class SettingsScreen(Screen):

    # store the instance of this class
    instance = None

    def __init__(self, *args, **kwargs):
        super(SettingsScreen, self).__init__(*args, **kwargs)
        SettingsScreen.instance = self
        self.name = "settings"
        self.sw_audio = SwitchButton(label="Audio", size_hint=(.3, 1))
        self.sw_audio.switch.bind(active=self.on_audio_active)
        self.sw_zone_sort = SwitchButton(label="Show Zonal Jobs only", size_hint=(.3, 1))
        self.sw_zone_sort.switch.bind(active=self.on_zone_jobs_only_active)
        self.sw_icab_verbose = SwitchButton(label="iCabbi Verbose", size_hint=(.3, 1))
        self.sw_icab_verbose.switch.bind(active=self.on_verbose_active)
        self.bidding_range = BiddingRangeWidget()
        self.driverbox = DriverWidget()
        self.debugbox = DebugWidget()
        self.satnav = SatNavWidget()
        gd_layout = GridLayout(rows=7, size_hint=(.8, .9), pos_hint={"center_x": .5, "center_y": .5})
        gd_layout.add_widget(self.debugbox)
        gd_layout.add_widget(self.driverbox)
        gd_layout.add_widget(self.satnav)
        gd_layout.add_widget(self.sw_audio)
        gd_layout.add_widget(self.sw_zone_sort)
        gd_layout.add_widget(self.sw_icab_verbose)
        gd_layout.add_widget(self.bidding_range)
        self.add_widget(gd_layout)

        self.debug_mode = False
    
    def on_enter(self, *args):
        """ initialize widgets from settings dict """
        settings = Globals.settings
        self.sw_audio.switch.active = Globals.settings["audio"]
        self.sw_icab_verbose.switch.active = Globals.settings["icabbi_verbose_mode"]
        self.sw_zone_sort.switch.active = Globals.settings.get("zone_jobs_only", True)
        self.bidding_range.slider.value = Globals.settings["bidding_radius"]
        
        self.driverbox.set_driver_id(Globals.settings["driver_id"])
        self.debug_mode = self.driverbox.set_host(Globals.settings["host"])
        self.debugbox.set_ip_and_port(Globals.settings["debug_ip"], Globals.settings["debug_port"])
        if Globals.settings["satnav"] == "waze":
            self.satnav.btn_satnav.text = "Waze"
        else:
            self.satnav.btn_satnav.text = "Google"

    def on_leave(self, *args):
        """ Grab string variables from widgets and store into settings dict and save to json file before leaving """
        settings = Globals.settings
        Globals.settings["bidding_radius"] = self.bidding_range.slider.value
        Globals.settings["driver_id"] = self.driverbox.txt_driverid.text
        handler.send_message(event=handler.EVENT_DRIVER_UPDATE, driver_id=Globals.settings["driver_id"])
        if self.driverbox.host:
            if self.debug_mode:
                ip, port = self.debugbox.get_ip_and_port()
                self.driverbox.host = f"http://{ip}:{port}"
                Globals.settings["debug_ip"] = ip
                Globals.settings["debug_port"] = port
            Globals.settings["host"] = self.driverbox.host
            handler.send_message(event=handler.EVENT_HOST_UPDATE, host=Globals.settings["host"])
        if self.satnav.btn_satnav.text == "Waze":
            Globals.settings["satnav"] = "waze"
        else:
            Globals.settings["satnav"] = "google"
        Globals.mainscrn.set_running_mode_label()
        save_settings(Globals.settings)
        return super().on_leave(*args)

    def on_audio_active(self, *args):
        """ store audio bool and save to json file """
        Globals.settings["audio"] = args[0].active
        save_settings(Globals.settings)
    
    def on_verbose_active(self, *args):
        Globals.settings["icabbi_verbose_mode"] = args[0].active
        save_settings(Globals.settings)
    
    def on_zone_jobs_only_active(self, *args):
        Globals.settings.setdefault("zone_jobs_only", args[0].active)
        save_settings(Globals.settings)


def check_value_isdigit(instance, value):
    if len(value) > 0:
        if not value[-1].isdigit():
            instance.text = instance.text[:-1]