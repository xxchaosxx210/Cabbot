from kivy.app import App
from kivy.base import EventLoop
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager

import icabbi

import time
import os
import json

class Settings:
    props = {}
    filename = "client_gui_settings.json"


def load_settings():
    if not os.path.exists(Settings.filename):
        Settings.props = {
                        "ip": "192.168.0.13", 
                        "port": "5000", 
                        "driverid": "19152" }
        Settings.props["host"] = "http://{}:{}".format(Settings.props["ip"], Settings.props["port"])
        Settings.props["debughost"] = "{}/debug/{}".format(Settings.props["host"], Settings.props["driverid"])
    else:
        with open(Settings.filename, "r") as fp:
            Settings.props = json.loads(fp.read())


Builder.load_string('''

<NetworkTextInput@TextInput>
    font_size: "22sp"
    text_size: self.size
    valign: "center"
    halign: "center"

<NetworkLabel@Label>:
    font_size: "18sp"
    size_hint: .1, 1

<NetworkConfigScreen>:
    ip: ip_id.text
    port: port_id.text
    driver_id: driverid_id.text
    BoxLayout:
        orientation: "vertical"
        size_hint: .5, .3
        pos_hint: {"center_y": .5, "center_x": .5}
        GridLayout:
            cols: 2
            rows: 3
            size_hint: 1, .9
            NetworkLabel:
                text: "IP: "
            NetworkTextInput:
                id: ip_id
                text: root.ip
            NetworkLabel:
                text: "Port: "
            NetworkTextInput:
                id: port_id
                text: root.port
            NetworkLabel:
                text: "Driver ID: "
            NetworkTextInput:
                id: driverid_id
                text: root.driver_id
        Button:
            size_hint: None, None
            size: 100, 60
            pos_hint: {"center_x": .5}
            text: "Continue"
            on_release: root.on_continue(self)


<ClientButton@Button>:


<ClientCommandScreen>:
    GridLayout:
        cols: 2
        rows: 4
        ClientButton:
            text: "Toggle Random Bids"
            on_release: root.on_rand_bids()
        ClientButton:
            text: "Offer Job"
            on_release: root.on_job_offer()
        ClientButton:
            text: "Change Status"
        ClientButton:
            text: "Replot"
            on_release: root.on_replot_button()
        ClientButton:
            text: "Toggle Pre-Bookings"
        ClientButton:
            text: "Remove Driver"
        ClientButton:
            text: "Booking Info"
        ClientButton:
            text: "Driver Status"
''')


class NetworkConfigScreen(Screen):

    ip = StringProperty("")
    port = StringProperty("")
    driver_id = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(NetworkConfigScreen, self).__init__(*args, **kwargs)
        self.name = "NetworkConfig"
        self.ip = Settings.props["ip"]
        self.port = Settings.props["port"]
        self.driver_id = Settings.props["driverid"]
    
    def on_continue(self, instance):
        Settings.props["host"] = "http://{}:{}".format(self.ip, self.port)
        Settings.props["driverid"] = self.driver_id
        Settings.props["ip"] = self.ip
        Settings.props["port"] = self.port
        ClientApp.instance.root.current = "ClientCommand"
        Settings.props["debughost"] = "{}/debug/{}".format(Settings.props["host"], self.driver_id)
        with open(Settings.filename, "w") as fp:
            fp.write(json.dumps(Settings.props))
        url = "{}/create-driver/{}".format(Settings.props["host"], Settings.props["driverid"])
        print(icabbi.http_request(url, None, "GET"))


class ClientCommandScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(ClientCommandScreen, self).__init__(*args, **kwargs)
        self.name = "ClientCommand"

    def on_replot_button(self):
        print(icabbi.setstatus(Settings.props["driverid"], Settings.props["host"], "1", "3"))

    def on_job_offer(self):
        print(icabbi.http_request(Settings.props["debughost"], {"type": "job-offer"}, "POST"))
    
    def on_rand_bids(self):
        print(icabbi.http_request(Settings.props["debughost"], {
            "type": "random-bids", 
            "enable": str(int(ClientApp.random_bid_enable))}, "POST"))
        ClientApp.random_bid_enable = not ClientApp.random_bid_enable


class ClientApp(App):

    instance = None
    handler = None
    random_bid_enable = True

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self.on_key_press)

    def build(self):
        load_settings()
        screenmanager = ScreenManager()
        screen = NetworkConfigScreen()
        screenmanager.add_widget(screen)
        screen = ClientCommandScreen()
        screenmanager.add_widget(screen)
        return screenmanager
    
    def on_key_press(self, window, key, *args):
        # 27 = Escape or Back key
        return True


def main():
    ClientApp.instance = ClientApp()
    ClientApp.instance.run()

if __name__ == "__main__":
    main()