from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.metrics import dp
from kivy.graphics import Color
from kivy.graphics import Rectangle


class HeaderViewContainer(BoxLayout):

    def __init__(self, **kwargs):
        super(HeaderViewContainer, self).__init__(**kwargs)

        self.orientation = "vertical"
        header_grid = GridLayout(cols=3, size_hint_y=.1)
        label = HeaderLabel(text="Zone")
        header_grid.add_widget(label)
        label = HeaderLabel(text="Jobs")
        header_grid.add_widget(label)
        label = HeaderLabel(text="Drivers")
        header_grid.add_widget(label)
        self.add_widget(header_grid)

        self.add_widget(ListCtrlBorder())
        
        self.column_rv = ColumnRecycleView()
        self.column_rv.viewclass = "RowViewContainer"
        self.add_widget(self.column_rv)


class HeaderLabel(Label):
    
    def __init__(self, **kwargs):
        super(HeaderLabel, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.6, 0.7, 0.4, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update, size=self.update)
    
    def update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ColumnRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(ColumnRecycleView, self).__init__(**kwargs)
        rbox_layout = RecycleBoxLayout(orientation="vertical",
        default_size=(None, dp(30)),
        default_size_hint=(1, None),
        size_hint_y=None)
        rbox_layout.bind(minimum_height=rbox_layout.setter("height"))
        self.add_widget(rbox_layout)    

    
    def populate(self, zones):
        self.data = []
        for zone in zones:
            d = {"zone": {"text": zone["name"]}, 
            "jobs": {"text": zone["job_count"]}, 
            "drivers": {"text": zone["total"]}}
            self.data.append(d)


class RowViewContainer(RecycleDataViewBehavior, BoxLayout):

    def __init__(self, **kwargs):
        super(RowViewContainer, self).__init__(**kwargs)
        vbox = BoxLayout(orientation="vertical")

        header_hbox = BoxLayout(orientation="horizontal")
        self.lbl_zone = Label(text="")
        header_hbox.add_widget(self.lbl_zone)
        self.lbl_jobs = Label(text="")
        header_hbox.add_widget(self.lbl_jobs)
        self.lbl_drivers = Label(text="")
        header_hbox.add_widget(self.lbl_drivers)

        vbox.add_widget(header_hbox)
        
        vbox.add_widget(ListCtrlBorder())

        self.add_widget(vbox)

    
    def refresh_view_attrs(self, rv, index, data):
        self.lbl_zone.text = data["zone"]["text"]
        self.lbl_jobs.text = data["jobs"]["text"]
        self.lbl_drivers.text = data["drivers"]["text"]
        return super(RowViewContainer, self).refresh_view_attrs(rv, index, data)


class ListCtrlBorder(BoxLayout):
    def __init__(self, **kwargs):
        super(ListCtrlBorder, self).__init__(**kwargs)
        self.size_hint = (1, .01)
        self.orientation = "horizontal"
        with self.canvas.before:
            Color(.7, .7, .7, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update, size=self.update)
    
    def update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ListCtrlApp(App):
    def build(self):
        from kivy.uix.button import Button
        self.header = HeaderViewContainer()
        box = BoxLayout(orientation="vertical")

        btn = Button(text="Refresh", size_hint=(1, .1))
        btn.bind(on_release=self._on_button_press)
        box.add_widget(self.header)
        box.add_widget(btn)
        return box
    
    def _on_button_press(self, *args):
        from icabbi import icabbi
        zones = icabbi.getzones("19152", icabbi.UK6)
        zoneids = icabbi.getzoneids("19152", icabbi.UK6)
        for zone in zones:
            zone["name"] = zoneids.get(zone["id"])
        self.header.column_rv.populate(zones)

if __name__ == '__main__':
    app = ListCtrlApp()
    app.run()