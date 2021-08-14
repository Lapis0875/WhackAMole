from typing import Optional, Final, ClassVar

import kivy
from kivy.app import App
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from random import choice
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '600')
Config.set('kivy', 'window_icon', '../../resources/icon.ico')
Config.write()
LabelBase.register(
    name='Cookierun',
    fn_regular='resources/fonts/Cookierun Regular.ttf',
    fn_italic='resources/fonts/Cookierun Regular.ttf',
    fn_bold='resources/fonts/Cookierun Black.ttf',
    fn_bolditalic='resources/fonts/Cookierun Black.ttf'
)


class ColorPallet:
    Green: Final[str] = '#6CE964'
    Red: Final[str] = '#E96464'
    Gray: Final[str] = '#404040'
    White: Final[str] = '#FFFFFF'
    Black: Final[str] = '#000000'


class WamControlBox(BoxLayout):
    def __init__(self, *, ui_controller = None, **kwargs):
        super(WamControlBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.ui_controller = ui_controller

        self.start_btn = Button(text='start', font_size=20, font_name='Cookierun', background_color=ColorPallet.Green)
        self.start_btn.bind(on_press=self.handle_btn_click)
        self.add_widget(self.start_btn)

        self.event_temp_btn = Button(text='temporary event viewer checker', font_size=20, font_name='Cookierun')
        self.random_event_texts = ('GameEvent Temp Text 01', 'Lorem ipsum.', 'Game Event Viewer Test Called.')
        self.event_temp_btn.bind(on_press=lambda btn: self.parent.info.event_holder.add_widget(
            Label(
                text=choice(self.random_event_texts),
                font_size=20,
                font_name='Cookierun'
            )))
        self.add_widget(self.event_temp_btn)

    def handle_btn_click(self, btn: Button):
        if self.ui_controller is None:
            self.ui_controller = self.parent.ui_controller
        if self.ui_controller.game_manager.current_session:
            # Session is running. Handle `stop_game`
            return self.stop_game(btn)
        else:
            # No running GameSession exists. Create new one.
            return self.start_game(btn)

    def start_game(self, btn: Button):
        # self.ui_controller.start_game()
        self.update_stop_btn(btn)
        self.ui_controller.start_test_game()

    def stop_game(self, btn: Button):
        self.update_start_btn(btn)
        self.ui_controller.stop_game()

    @staticmethod
    def update_start_btn(btn: Button):
        btn.opacity = 0.5
        btn.background_color = ColorPallet.Green
        btn.text = 'Start Game'
        btn.opacity = 1

    @staticmethod
    def update_stop_btn(btn: Button):
        btn.opacity = 0.5
        btn.background_color = ColorPallet.Red
        btn.text = 'Stop Game'
        btn.opacity = 1

    def set_btn_green(self):
        # start_btn color changer.
        # macro method for changing color, to reduce imports. (import of ColorPallet), and
        self.update_start_btn(self.start_btn)


class WamEventBox(BoxLayout):
    def __init__(self, **kwargs):
        super(WamEventBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.event_logs: list[Label] = []   # list to store event logs.
    
    def add_widget(self, widget, index=0, canvas=None):
        self.event_logs.append(widget)      # Register event log in list.
        return super(WamEventBox, self).add_widget(widget, index, canvas)       # Call parent class's add_widget logic.

    def get_event_log(self, index: int) -> Optional[Label]:
        try:
            return self.event_logs[index]
        except IndexError:
            return None


class WamInfoBox(BoxLayout):
    def __init__(self, **kwargs):
        super(WamInfoBox, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.event_view = ScrollView(scroll_type=['bars'], do_scroll_x=False, do_scroll_y=True, bar_margin=5)
        self.event_holder = WamEventBox()
        self.event_view.add_widget(self.event_holder)
        self.add_widget(self.event_view)


class WamMainBox(BoxLayout):
    def __init__(self, *, ui_controller=None, **kwargs):
        super(WamMainBox, self).__init__(**kwargs)
        self.ui_controller = ui_controller
        self.orientation = 'horizontal'

        self.control = WamControlBox(ui_controller=self.ui_controller)
        self.add_widget(self.control)
        self.info = WamInfoBox()
        self.add_widget(self.info)


class WamApp(App):
    def __init__(self, ui_controller=None, **kwargs):
        super(WamApp, self).__init__(**kwargs)
        self.ui_controller = ui_controller
        self.main_box = None
        ui_controller.bind_app(self)

    def build(self):
        self.title = '디지털공작소 두더지 잡기 배틀'
        self.icon = 'resources/icon.png'
        self.main_box = WamMainBox(ui_controller=self.ui_controller)
        self.write_event_log('두더지 잡기 배틀 GUI 실행됨.')
        return self.main_box

    def write_event_log(self, text: str):
        self.main_box.info.event_holder.add_widget(Label(text=text, font_size=10, font_name='Cookierun'))

    def bind_ui_controller(self, ui_controller):
        if self.ui_controller:
            raise ValueError('WamApp.ui_controller is already bound!')
        self.ui_controller = ui_controller


if __name__ == '__main__':
    WamApp().run()
