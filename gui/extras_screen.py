from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from dialogs import AboutDialog
from dialogs import DumpDialog

from globals import Globals
from globals import handler


class ExtrasScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(ExtrasScreen, self).__init__(**kwargs)
        self.name = "extras"
        btn_kick = Button(text="Kick Drivers", on_release=self.on_kick_driver_button)
        btn_messages = Button(text="Messages", on_release=self.on_message_button)
        btn_bookings = Button(text="Bookings", on_release=self.on_bookings_button_press)
        btn_log = Button(text="Log", on_release=self.on_log_button_press)
        btn_about = Button(text="About", on_release=self.on_about_button_press)

        grid_layout = GridLayout(cols=1, rows=5)
        grid_layout.size_hint = (.5, .5)
        grid_layout.pos_hint = {"center_x": .5, "center_y": .5}
        grid_layout.add_widget(btn_kick)
        grid_layout.add_widget(btn_messages)
        grid_layout.add_widget(btn_bookings)
        grid_layout.add_widget(btn_log)
        grid_layout.add_widget(btn_about)
        self.add_widget(grid_layout)
    
    def on_bookings_button_press(self, instance):
        Globals.app.root.current = "history"
    
    def on_kick_driver_button(self, instance):
        Globals.app.root.current = "status"
        handler.send_message(event=handler.EVENT_KICK_DRIVERS)
    
    def on_about_button_press(self, instance):
        dlg = AboutDialog()
        dlg.open()
    
    def on_message_button(self, instance):
        handler.send_message(event=handler.EVENT_MESSAGE_ARCHIVE)
        Globals.app.root.current = "messages"
    
    def on_log_button_press(self, instance):
        dlg = DumpDialog()
        dlg.open()