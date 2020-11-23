from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.metrics import sp
from kivy.metrics import dp
from kivy.metrics import pt
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout

from kivytoast import toast as _kivy_toast

from globals import __author__, __title__, __date__, __version__
from globals import handler
from globals import Globals

from pydroid import is_android
from pydroid import insert_contact as _droid_insert_contact
from pydroid import phone_call as _droid_phone_call
from pydroid import toast as _droid_toast


Builder.load_string('''
<WrappedLabel>:
    text_size: self.width, None
    height: self.texture_size[1]

<ScrollableLabel>:
    markup: False
    text_size: self.width, None
    height: self.texture_size[1] + 15
    size_hint_y: None
    font_size: "20sp"
''')


def show_toast(message="", long_time=False):
    if is_android():
        _droid_toast(message)
    else:
        _kivy_toast(message, long_time)


class ScrollableLabel(Label):
    pass


class ScrollableView(ScrollView):

    def __init__(self, **kwargs):
        super(ScrollableView, self).__init__(**kwargs)
        self.history = ScrollableLabel(text="")
        self.add_widget(self.history)


class DumpDialog(Popup):

    def __init__(self, **kwargs):
        super(DumpDialog, self).__init__(**kwargs)
        self.autodismiss = True
        self.title = "Dump"
        self.sv = ScrollableView()
        gd_layout = GridLayout(cols=2, size_hint=(.5, .2), pos_hint={"center_x": .5})
        copy_button = Button(text="Copy", on_release=self.on_copy_button)
        copy_button.size_hint = (.5, .2)
        close_button = Button(text="Close", on_release=self.dismiss)
        close_button.size_hint = (.5, .2)
        gd_layout.add_widget(copy_button)
        gd_layout.add_widget(close_button)

        vbox = BoxLayout(orientation="vertical")
        vbox.add_widget(self.sv)
        vbox.add_widget(gd_layout)
        self.add_widget(vbox)
    
    def on_copy_button(self, instance):
        Clipboard.copy(self.sv.history.text)
        show_toast("Data has been copied to clipboard")
    
    def on_open(self):
        with open(Globals.DUMP_FILEPATH, "r") as fp:
            self.sv.history.text = fp.read()


class BusyDialog(Popup):
    
    def __init__(self, **kwargs):
        super(BusyDialog, self).__init__(**kwargs)
        self.autodismiss = False
        self.size_hint = (None, None)
        self.size = (dp(500), dp(200))
        self.title = "Driver Login"

        btn_login = Button(text="Login", on_release=self.on_button_pressed, id="login")
        btn_break = Button(text="Break", on_release=self.on_button_pressed, id="break")
        btn_logout = Button(text="Logout", on_release=self.on_button_pressed, id="logout")
        btn_close = Button(text="Close", on_release=self.dismiss)

        grid_layout = GridLayout(cols=4, rows=1)
        for widget in [btn_login, btn_break, btn_logout, btn_close]:
            grid_layout.add_widget(widget)
        self.add_widget(grid_layout)

    def on_button_pressed(self, instance):
        i = instance.id
        if i == "login":
            status, reason = ("1", "1")
        elif i == "break":
            status, reason = ("3", "2")
        else:
            status, reason = ("3", "3")
        handler.send_message(event=handler.EVENT_DRIVER_UPDATE, status=status, reason=reason)
        self.dismiss()


class LoadingDialog(Popup):

    def __init__(self, *args, **kwargs):
        super(LoadingDialog, self).__init__(*args, **kwargs)
        self.auto_dismiss = False
        self.size_hint = (None, None)
        self.size = (int(Window.width/1.2), int(Window.height/1.2))
        self.title = ""
        self.label = Label(text="", size_hint=(1, 1))
        self.label.texture_size = self.size
        self.label.font_size = pt(20)
        self.dot_count = 0
        self.is_open = False
        self.add_widget(self.label)
    
    def on_loading(self, *args):
        self.dot_count += 1
        if self.dot_count == 12:
            self.dot_count = 0
            self.label.text = "Loading \n"
        else:
            self.label.text += "."
    
    def on_open(self):
        self.is_open = True
        self.reset()
        self.loading = Clock.schedule_interval(self.on_loading, 0.2)
    
    def on_dismiss(self):
        self.is_open = False
        self.reset()
        self.loading.cancel()
    
    def reset(self):
        self.dot_count = 0
        self.label.text = "Loading \n"


class EarningsDialog(Popup):

    def __init__(self, **kwargs):
        super(EarningsDialog, self).__init__(**kwargs)
        self.autodismiss = False
        self.size_hint = (None, None)
        self.size = (int(Window.width/1.2), int(Window.height/1.2))
        self.title = "Earnings"
        
        self.label = Label(text="",
                            size_hint=(1, .9))
        btn_close = Button(text="Close", size_hint=(1, .1), on_release=self.dismiss)

        box = BoxLayout(orientation="vertical")
        box.add_widget(self.label)
        box.add_widget(btn_close)
        self.add_widget(box)

    def on_open(self):
        """retrieve booking archive"""
        Globals.earnings_dialog = self
        Globals.loading_dialog.open()
        handler.send_message(event=handler.EVENT_BOOKING_ARCHIVE, offsets=["0", "100", "200"])
    
    def on_dismiss(self):
        Globals.earnings_dialog = None
    
    def display_earnings(self, takings):
        Globals.loading_dialog.dismiss()
        for key, value in list(takings.items()):
            self.label.text += f"{key}: {value} \n \n"


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):

    def __init__(self, **kwargs):
        super(SelectableRecycleBoxLayout, self).__init__(**kwargs)
        self.default_size = (None, dp(100))
        self.default_size_hint = (1, None)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.orientation = "vertical"


class WrappedLabel(Label):
    pass


class InfoDialog(Popup):
    """Phone information dialog box"""

    def __init__(self, **kwargs):
        super(InfoDialog, self).__init__(**kwargs)
        self.auto_dismiss = False
        self.size_hint = (None, None)
        self.size = (int(Window.width/1.2), int(Window.height/1.2))

        class LabelInfo(Label):
            def __init__(self, **kwargs):
                super(LabelInfo, self).__init__(**kwargs)
                self.spacing = (0, 0, 0, 0)
                self.font_size = sp(18)

        lbl_customer = LabelInfo(text="Customer Name:")
        self.lbl_customer_name = LabelInfo(text="")
        lbl_phone = LabelInfo(text="Phone Number:")
        self.lbl_phone_number = LabelInfo(text="")

        btn_call = Button(text="Call", on_release=self.on_call)
        btn_copy = Button(text="Copy", on_release=self.on_copy)
        btn_add = Button(text="Add", on_release=self.on_add)
        btn_close = Button(text="Close", on_release=self.dismiss)

        # layout
        vbox = BoxLayout(orientation="vertical", padding=(0,0,0,0))
        row1 = BoxLayout(orientation="horizontal", size_hint=(1, .4))
        row2 = BoxLayout(orientation="horizontal", size_hint=(1, .4))
        row3 = BoxLayout(orientation="horizontal", size_hint=(1, .2))

        row1.add_widget(lbl_customer)
        row1.add_widget(self.lbl_customer_name)
        vbox.add_widget(row1)

        row2.add_widget(lbl_phone)
        row2.add_widget(self.lbl_phone_number)
        vbox.add_widget(row2)

        row3.add_widget(btn_call)
        row3.add_widget(btn_copy)
        row3.add_widget(btn_add)
        row3.add_widget(btn_close)
        vbox.add_widget(row3)

        self.add_widget(vbox)
    
    def on_copy(self, instance):
        Clipboard.copy(self.lbl_phone_number.text)
        #show_toast(f"{self.lbl_phone_number.text} has been copied to the clipboard")
    
    def on_call(self, instance):
        if self.lbl_phone_number.text:
            _droid_phone_call(self.lbl_phone_number.text)
    
    def on_add(self, instance):
        if self.lbl_phone_number.text:
            _droid_insert_contact(self.lbl_customer_name.text, self.lbl_phone_number.text)
    
    def set_phone_and_name(self, name, phone):
        self.lbl_customer_name.text = name
        self.lbl_phone_number.text = phone


class AboutDialog(Popup):
    
    def __init__(self, **kwargs):
        super(AboutDialog, self).__init__(**kwargs)
        self.autodismiss = False
        self.title = "About"
        self.size_hint = (None, None)
        
        lbl = Label(size_hint=(1, .9))
        self.size=lbl.texture_size
        lbl.text = f"Title: {__title__} \n \nAuthor: {__author__} \n \nDate: {__date__} \n \nVersion: {__version__}"
        btn = Button(text="Close", size_hint=(1, .1), on_release=self.dismiss)

        vbox = BoxLayout(orientation="vertical")
        vbox.add_widget(lbl)
        vbox.add_widget(btn)

        self.add_widget(vbox)

        self.size = ((Window.width / 1.2), (Window.height / 1.2))


class MessageDialog(Popup):

    def __init__(self, **kwargs):
        super(MessageDialog, self).__init__(**kwargs)
        self.auto_dismiss = False
        self.size_hint = (None, None)
        self.size  = (int(Window.width / 1.2), int(Window.height / 2))
        self.title = "Message #"

        self.message_label = WrappedLabel(text="", size_hint=(1, .8))

        btn_close = Button(text="Close", on_release=self.dismiss)
        btn_close.size_hint = (.4, .2)
        btn_close.pos_hint = {"center_x": .5}

        vbox = BoxLayout(orientation="vertical")
        vbox.add_widget(self.message_label)
        vbox.add_widget(btn_close)
        self.add_widget(vbox)

    def on_dismiss(self):
        Globals.message_dialog = None