#!/usr/bin/env python3
# -*- coding=utf-8 -*-

# add directories to the global python path
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "gui"))
sys.path.append(os.path.join(os.getcwd(), "icabbi"))

# Kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.logger import Logger
from kivy.base import EventLoop
from kivy.clock import mainthread
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import WipeTransition

from gui.listctrl import HeaderViewContainer

from globals import Globals
from globals import load_settings
from globals import save_settings
from globals import handler
from globals import dump_to_file

from gui.host_screen import HostScreen
from gui.extras_screen import ExtrasScreen
from gui.messages_screen import MessagesScreen
from gui.job_history_screen import JobHistoryScreen
from gui.status_screen import StatusScreen
from gui.settings_screen import SettingsScreen
from gui.dialogs import show_toast
from gui.dialogs import MessageDialog
from gui.dialogs import LoadingDialog

import threading
import time
import json

from pydroid import ask_permission as android_ask_permission
from pydroid import navigate_google_maps
from pydroid import navigate_waze


Builder.load_string('''
<Label>:
    bold: True

<Widget>:
    font_size: "14sp"
''')


class CabBotApp(App):
    """
    Main app most of the global variable initializing starts here
    """
    def on_start(self):
        """
        initialize settings and start cabbot thread
        """
        for name in os.environ.keys():
            print("{}: {}".format(name, os.environ[name]))
        Globals.settings = load_settings()
        with open(Globals.DUMP_FILEPATH, "w") as fp:
            fp.write(f"Path={os.getcwd()} \n \n")
        Globals.app = self
        EventLoop.window.bind(on_keyboard=self.on_keyboard_press)
        # intialize global loading dialog
        Globals.loading_dialog = LoadingDialog()
        Globals.icabthread = threading.Thread(
            target=handler.thread_handler,
            kwargs={
                "driverid": Globals.settings["driver_id"],
                "host": Globals.settings["host"],
                "callback": on_handler_event
            }
        )
        #self.logcat = LogCatReader(None)
        #self.logcat.start()
        Globals.icabthread.start()
        handler.send_message(event=handler.EVENT_DRIVER_UPDATE, driver_id=Globals.settings["driver_id"])
        # ask for phone permissions
        if Globals.settings["android_run_first_time"]:
            timeout = 5
            Globals.settings["android_run_first_time"] = False
            save_settings(Globals.settings)
        else:
            timeout = 0
        android_ask_permission(["android.permission.ACCESS_FINE_LOCATION"], timeout)

    def on_stop(self):
        show_toast("Closing CabBot please wait...")
        handler.send_message(event=handler.EVENT_QUIT)
        while Globals.icabthread.isAlive():
            pass
    
    def on_pause(self):
        # when screen is running in background pause thread
        handler.send_message(event=handler.EVENT_PAUSE_THREAD, pause=True)
        return True

    def on_resume(self):
        # restart thread
        handler.send_message(event=handler.EVENT_PAUSE_THREAD, pause=False)

    def on_keyboard_press(self, window, key, *largs):
        if key == 27:
            if self.root.current == "settings":
                self.root.current = "status"
            elif self.root.current == "messages":
                self.root.current = "extras"
            elif self.root.current == "history":
                self.root.current = "extras"
            elif self.root.current == "extras":
                self.root.current = "status"
            elif self.root.current == "status":
                #self.logcat.quit.set()
                return False
        return True

    def build(self):
        screenmanager = ScreenManager()
        screenmanager.transition = WipeTransition()
        screen = HostScreen()
        screenmanager.add_widget(screen)
        screen = StatusScreen()
        screenmanager.add_widget(screen)
        screen = ExtrasScreen()
        screenmanager.add_widget(screen)
        screen = JobHistoryScreen()
        screenmanager.add_widget(screen)
        screen = MessagesScreen()
        screenmanager.add_widget(screen)
        screen = SettingsScreen()
        screenmanager.add_widget(screen)
        return screenmanager


def format_booking(booking):
    """ formats booking dict properties to string and displays to Kivy Label """
    payment = getattr(booking, "payment", {"meter": "0", "fee": "0"})
    if hasattr(payment, "meter"):
        price = payment["meter"]
    else:
        price = payment["fee"]
    name = booking["user"].get("name", "unknown")
    phone = booking["user"].get("phone", "0")
    direct_connect = booking["user"].get("direct_connect")
    address_latitude = booking.get("lat", 0.0)
    address_longitude = booking.get("lng", 0.0)
    if "data" in booking:
        address = booking["data"].get("address", "")
        destination = booking["data"].get("destination", "")
        destination_latitude = booking["data"].get("destination_lat", 0.0)
        destination_longitude = booking["data"].get("destination_lng", 0.0)
    else:
        address = ""
        destination = ""
        destination_latitude = 0.0
        destination_longitude = 0.0
    if "config" in booking:
        satnav_query = booking["config"].get("satnav_query")
    else:
        satnav_query = ""
    address_ref = {
                    "address": address, 
                    "lat": address_latitude, 
                    "lng": address_longitude,
                    "satnav_query": satnav_query}
    destination_ref = {
                        "destination": destination, 
                        "lat": destination_latitude, 
                        "lng": destination_longitude, 
                        "username": name}
    s = {}
    s["Name"] = name
    s["Phone"] = '''[ref={"phone":"%s", "name": "%s"}][color=#66CCFF]%s[/color][/ref]''' % (phone, name, phone)
    s["direct_connect"] = '''[ref={"direct":"%s", "name":"%s"}][color=#449922]%s[/color][/ref]''' \
    % (direct_connect, name, direct_connect)
    s["Address"] = '[ref=%s]%s[/ref]' % (json.dumps(address_ref), address)
    s["Destination"] = '[ref=%s]%s[/ref]' % (json.dumps(destination_ref), destination)
    s["Pickup"] = time.ctime(booking.get("pickup_date", 0))
    s["Fee"] = price
    return s


@mainthread
def on_handler_event(resp):
    """
    events triggered from the icabbi handler thread are caught here
    """
    # CHANGED HOST
    if resp.event == handler.EVENT_HOST_UPDATE:
        Logger.info("Host is now {host}".format(host=resp.host))
    # CHANGED DRIVER ID
    elif resp.event == handler.EVENT_DRIVER_UPDATE:
        if hasattr(resp, "driver_id"):
            Logger.info("New driver ID #{_id}".format(_id=resp.driver_id))
    # NEW BID
    elif resp.event == handler.EVENT_BID_UPDATE:
        sv = Globals.mainscrn.ids.get("sv_namevalue")
        sv.add("Bid: ", "{} ({})".format(resp.bid["title"], resp.bid["distance"]))
    # NOW ON JOB
    elif resp.event == handler.EVENT_NEW_JOB:
        sv = Globals.mainscrn.ids.get("sv_namevalue")
        sv.clear()
        for name, value in tuple(format_booking(resp.booking).items()):
            sv.add(name + ": ", value)
            if name == "Phone" or name == "Address" or name == "direct_connect":
                sv.add("", "")
        sv.add("", '''[ref={"action":"arrived","booking_id":"%s"}][color=#FFD919]Notify Customer[/color][/ref]''' % resp.booking["id"])
        sv.add("", '''[ref={"action":"madecontact", "booking_id": "%s"}][color=#E67300]Picked up Customer[/color][/ref]''' % resp.booking["id"])
    # JOB HAS BEEN OFFERED
    elif resp.event == handler.EVENT_JOB_OFFER:
        if hasattr(resp, "accepted"):
            if Globals.settings["audio"]:
                Globals.android_play_system_sound("notification")
                Globals.android_text2speak.speak("Job offer has been accepted.")
            show_toast("Job offer has been accepted...")
    # LOGGED OUT
    elif resp.event == handler.EVENT_LOGGED_OUT:
        sv = Globals.mainscrn.ids["sv_namevalue"]
        sv.clear()
        sv.add("Driver Status: ", "Logged out")
    # ALL ZONES CHANGED
    elif resp.event == handler.EVENT_ZONES:
        # if status screen then show zone update
        if Globals.app.root.current == "status":
            # get the listctrl window
            listctrl = Globals.app.root.current_screen.ids.get("headerview_id")
            listctrl.column_rv.populate(resp.zones)
    # ZONE HAS CHANGED
    elif resp.event == handler.EVENT_ZONE_UPDATE:
        zone = resp.zone
        sv = Globals.mainscrn.ids.get("sv_namevalue")
        sv.clear()
        sv.add("Zone: ", zone.get("title"))
        sv.add("Id: ", zone.get("id"))
        sv.add("Position: ", zone.get("position"))
        sv.add("Drivers: ", zone.get("total"))
        sv.add("Jobs: ", zone.get("job_count"))
    # QUITING
    elif resp.event == handler.EVENT_QUIT:
        Logger.info("iCabbi thread has now closed.")
    # BOOKING UPDATED
    elif resp.event == handler.EVENT_BOOKING_UPDATE:
        #Globals.mainscrn.status_text = "Customer has been notified" if resp.status == "arrived" else "Picked up Customer"
        pass
    # ERROR
    elif resp.event == handler.EVENT_NETWORK_ERROR:
        if Globals.loading_dialog.is_open():
            Globals.loading_dialog.dismiss()
        sv = Globals.mainscrn.ids["sv_namevalue"]
        sv.clear()
        sv.add("[color=#FF0000]ERROR[/color]: ", resp.message)
    # PREBOOKINGS
    elif resp.event == handler.EVENT_PREBOOKINGS_UPDATE:
        pass
    # BOOKING ARCHIVE REQUEST
    elif resp.event == handler.EVENT_BOOKING_ARCHIVE:
        if Globals.earnings_dialog:
            Globals.earnings_dialog.display_earnings(resp.takings)
        elif Globals.app.root.current == "history":
            # history screen is open
            history_screen = Globals.app.root.get_screen("history")
            history_screen.load_bookings(resp.bookings, resp.takings)
    # KICKED DRIVER
    elif resp.event == handler.EVENT_KICK_DRIVERS:
        sv = Globals.mainscrn.ids.get("sv_namevalue")
        sv.add("[color=#ffff00]Kicking[/color]: ", resp.message)
    # MESSAGE ARCHIVE REQUEST
    elif resp.event == handler.EVENT_MESSAGE_ARCHIVE:
        for message in resp.messages:
            date_created = str(time.ctime(message["created"]))
            text = "{} - {}".format(date_created, str(message["message"]))
            Globals.message_list_view.data.append({
                "id": str(message["id"]), 
                "text": text})
    # EXTENDED MESSAGE REQUEST
    elif resp.event == handler.EVENT_MESSAGE:
        if Globals.message_dialog:
            print(resp.message)
            Globals.message_dialog.message_label.text = resp.message["message"]
    # SENT MESSAGE
    elif resp.event == handler.EVENT_MESSAGE_DISPATCH:
        if resp.message == "{}":
            show_toast("Message Sent")
        else:
            show_toast(resp.message)
    # BIDDING HAS CHANGED
    elif resp.event == handler.EVENT_CHANGE_BIDDING:
        sv = Globals.mainscrn.ids.get("sv_namevalue")
        sv.add("[color=#ffff00]Setting[/color]: ", f"Auto Bidding is set to {resp.enable}")
    # THREAD EXCEPTION
    elif resp.event == handler.EVENT_THREAD_EXCEPTION:
        if Globals.loading_dialog.is_open:
            Globals.loading_dialog.dismiss()
        dlg = MessageDialog()
        dlg.message_label.text = resp.error
        dlg.open()
    elif resp.event == handler.EVENT_CONNECTION_STATUS:
        slbl = Globals.mainscrn.ids.get("id_status_label")
        slbl.text = resp.text

def main():
    cabbot_app = CabBotApp()
    cabbot_app.run()


if __name__ == '__main__':
    main()
