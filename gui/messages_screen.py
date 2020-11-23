from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import mainthread
from kivy.uix.recycleview import RecycleView
from kivy.metrics import dp
from kivy.metrics import pt
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from dialogs import SelectableRecycleBoxLayout
from dialogs import MessageDialog

from globals import Globals
from globals import handler


class MessagesScreen(Screen):

    def __init__(self, **kwargs):
        super(MessagesScreen, self).__init__(**kwargs)
        self.name = "messages"

        self.message_input = TextInput(multiline=True, text="", font_size=pt(10))
        btn_send = Button(text="Send", size_hint=(.2, 1), on_release=self.on_send_button)
        btn_voice = Button(text="Voice", size_hint=(.2, 1), on_release=self.on_voice_message)

        vbox = BoxLayout(orientation="vertical")

        messagebar = GridLayout(cols=3, rows=1)
        messagebar.size_hint = (1, .3)
        messagebar.add_widget(self.message_input)
        messagebar.add_widget(btn_send)
        messagebar.add_widget(btn_voice)
        vbox.add_widget(messagebar)

        vbox.add_widget(BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(20)))

        # Create second row
        rc_messages = RecycleViewMessages()
        rc_messages.viewclass = "RecycleViewMessagesButton"
        vbox.add_widget(rc_messages)

        self.add_widget(vbox)
    
    def on_leave(self, *args):
        # reset the listview
        data = Globals.message_list_view.data
        while len(data) > 0:
            for x in range(len(data)):
                try:
                    data.pop(x)
                except IndexError:
                    pass
    
    def on_voice_message(self, instance):
        handler.Globals.droid_speech2txt.show_sp2txt_dialog(self.on_speech2text_reply)
    
    @mainthread
    def on_speech2text_reply(self, text):
        self.message_input.text = text
    
    def on_send_button(self, instance):
        handler.send_message(event=handler.EVENT_MESSAGE_DISPATCH, text=str(self.message_input.text))
        self.message_input.text = ""


class RecycleViewMessages(RecycleView):

    def __init__(self, **kwargs):
        super(RecycleViewMessages, self).__init__(**kwargs)
        self.add_widget(SelectableRecycleBoxLayout())
        Globals.message_list_view = self


class RecycleViewMessagesButton(RecycleDataViewBehavior, Button):

    def on_release(self):
        handler.send_message(event=handler.EVENT_MESSAGE, id=self.id)
        Globals.message_dialog = MessageDialog()
        Globals.message_dialog.open()