from kivy.config import Config
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from split_mp3 import split_mp3
from kivy.animation import Animation
from plyer import notification

Config.set('kivy', 'window_icon', 'icon.png')

class FileChooserPopup(Popup):
    def __init__(self, on_select, **kwargs):
        super().__init__(**kwargs)
        self.title = "Choose MP3 File"
        self.size_hint = (0.9, 0.9)
        chooser = FileChooserIconView(filters=["*.mp3", "*.wav", "*.m4a"])
        chooser.bind(on_submit=lambda instance, selection, touch: self.select_file(selection, on_select))
        self.content = chooser

    def select_file(self, selection, on_select):
        if selection:
            on_select(selection[0])
        self.dismiss()

class SplitterLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.drop_label = Label(
            text="⬇️ Drag and drop your MP3 here ⬇️",
            size_hint_y=None,
            height=60,
            color=(0.2, 0.6, 1, 1),
            bold=True
        )
        self.add_widget(self.drop_label, index=0)

        self.input = TextInput(hint_text="MP3 file path", size_hint_y=None, height=40)
        self.add_widget(self.input)

        browse_btn = Button(text="Browse", size_hint_y=None, height=40)
        browse_btn.bind(on_release=self.open_filechooser)
        self.add_widget(browse_btn)

        split_btn = Button(text="Split Audio", size_hint_y=None, height=40)
        split_btn.bind(on_release=self.split_audio)
        self.add_widget(split_btn)

        self.message = Label(text="", size_hint_y=None, height=30)
        self.add_widget(self.message)

        self.register_event_type('on_dropfile')
        self.bind(on_dropfile=self._on_file_drop)

    def open_filechooser(self, instance):
        FileChooserPopup(on_select=self.set_path).open()

    def set_path(self, path):
        self.input.text = path

    def split_audio(self, instance):
        path = self.input.text.strip()
        if not path:
            self.message.text = "Please select an audio file."
            return
        try:
            count = split_mp3(path)
            self.message.text = f"File split into {count} parts."
            from plyer import notification
            notification.notify(
                title="Split Complete",
                message=f"File split into {count} parts.",
                timeout=5
            )
        except Exception as e:
            self.message.text = f"Error: {str(e)}"

    def on_dropfile(self, *args):
        pass  # Required to register the event

    def _on_file_drop(self, instance, file_path_bytes):
        file_path = file_path_bytes.decode("utf-8")
        if file_path.endswith((".mp3", ".wav", ".m4a")):
            self.input.text = file_path
            self.message.text = "Audio file selected via drag-and-drop."
            anim = Animation(color=(0, 1, 0, 1), duration=0.5) + Animation(color=(0.2, 0.6, 1, 1), duration=0.5)
            anim.start(self.drop_label)
        else:
            self.message.text = "Only MP3 files are supported for drag-and-drop."

from kivy.core.window import Window

class MP3SplitterApp(App):
    def build(self):
        return SplitterLayout()

    def on_start(self):
        Window.allow_dropfile = True

if __name__ == "__main__":
    MP3SplitterApp().run()
