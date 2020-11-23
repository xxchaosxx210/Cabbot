from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import mainthread
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.lang import Builder

import time

from dialogs import InfoDialog

from globals import handler
from globals import Globals


Builder.load_string('''
<JobHistoryScrollView>:
    JobHistoryLabel:
        markup: True
        text: root.text
        text_size: self.width, None
        height: self.texture_size[1]
        size_hint_y: None
        font_size: "20sp"
''')


class JobHistoryScreen(Screen):
    bookings = []
    takings = {}
    MAX_OFFSET = 10
    offset_counter = 0

    def __init__(self, *args, **kwargs):
        super(JobHistoryScreen, self).__init__(**kwargs)
        self.name = "history"
        self.lbl_scroll = JobHistoryScrollView(text="")

        btn_prev = Button(text="<", on_release=self.on_prev)
        btn_next = Button(text=">", on_release=self.on_next)

        btn_retrieve = Button(text="Retrieve", on_release=self.on_retrieve_button)                               

        vbox = BoxLayout(orientation="vertical")

        # 1st row
        vbox.add_widget(self.lbl_scroll)

        # 2nd row
        row2 = BoxLayout(orientation="horizontal", size_hint=(1, .1))
        a_prev = AnchorLayout()
        a_next = AnchorLayout()
        a_prev.add_widget(btn_prev)
        a_next.add_widget(btn_next)
        row2.add_widget(a_prev)
        row2.add_widget(a_next)
        vbox.add_widget(row2)

        # 3rd row
        row3 = BoxLayout(orientation="horizontal", size_hint=(1, .2))
        anchor = AnchorLayout(anchor_x="center")
        anchor.add_widget(btn_retrieve)
        row3.add_widget(anchor)
        vbox.add_widget(row3)

        self.add_widget(vbox)

    def on_retrieve_button(self, instance):
        Globals.loading_dialog.open()
        handler.send_message(event=handler.EVENT_BOOKING_ARCHIVE, offsets=["0", "100", "200"])
    
    @mainthread
    def load_bookings(self, bookings, takings):
        if Globals.loading_dialog.is_open:
            Globals.loading_dialog.dismiss()
        JobHistoryScreen.bookings = bookings
        JobHistoryScreen.takings = takings
        JobHistoryScreen.offset_counter = 0
        self.display_bookings(0)
    
    def on_next(self, instance):
        if self.display_bookings(
            JobHistoryScreen.offset_counter + JobHistoryScreen.MAX_OFFSET):
            JobHistoryScreen.offset_counter += JobHistoryScreen.MAX_OFFSET
    
    def on_prev(self, instance):
        if self.display_bookings(
            JobHistoryScreen.offset_counter - JobHistoryScreen.MAX_OFFSET):
            JobHistoryScreen.offset_counter -= JobHistoryScreen.MAX_OFFSET
    
    def display_bookings(self, offset=0):
        if offset < 0:
            return False
        if offset >= len(JobHistoryScreen.bookings) + JobHistoryScreen.MAX_OFFSET:
            return False
        self.lbl_scroll.scroll_y = 1
        self.lbl_scroll.text = ""
        for index, booking in enumerate(JobHistoryScreen.bookings):
            if index >= offset and index <= offset + JobHistoryScreen.MAX_OFFSET:
                self.lbl_scroll.text += self.format_jobhistory_booking(booking)
        return True
    
    def format_jobhistory_booking(self, booking):
        if "user" not in booking:
            user = {"phone": "", "name": ""}
        else:
            user = booking["user"]
            user["name"] = user.get("name", "")
            user["phone"] = user.get("phone", "")
        if "payment" not in booking:
            payment = {"total": "0.0"}
        else:
            payment = booking["payment"]
            payment["total"] = payment.get("total", "0.0")
        buff = "Address:      {} \n".format(booking["address"])
        buff += "Destination:  {} \n".format(booking["destination"])
        buff += "Total:         {} \n".format(payment["total"])
        buff += "Name:         {} \n".format(user["name"])
        buff += """Phone:        [color=6666ff][ref=%s;%s]%s[/ref][/color] \n""" % (
            str(user["phone"]), 
            user["name"].capitalize(),
            user["phone"])
        if "pickup_date" in booking:
            _t = time.ctime(float(booking["pickup_date"]))
        else:
            _t = "VOID"
        buff += "Pickup:       {} \n \n \n".format(_t)
        return buff


class JobHistoryScrollView(ScrollView):
    text = StringProperty("")


class JobHistoryLabel(Label):

    def __init__(self, **kwargs):
        super(JobHistoryLabel, self).__init__(**kwargs)

    def on_ref_press(self, value):
        dlg = InfoDialog()
        dlg.title = "Phone number"
        phone, name = value.split(";")
        dlg.set_phone_and_name(name, phone)
        dlg.open()