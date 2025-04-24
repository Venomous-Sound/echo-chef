# 🧭 Entry point for EchoChef Splitter GUI
# Drag & drop MP3/WAV/M4A files here to auto-split if >8MB
# Triggered by autosplit_audio.py, requires ffmpeg in PATH
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase
import os
import platform
import subprocess
from chefbot_file_utils import split_mp3, convert_wav_to_mp3, convert_m4a_to_mp3

# Register emoji-compatible font (ensure DejaVuSans.ttf is in the project directory)
LabelBase.register(name="DejaVuSans", fn_regular="DejaVuSans.ttf")

def open_folder(path):
    if platform.system() == "Darwin":
        subprocess.call(["open", path])
    elif platform.system() == "Windows":
        subprocess.call(["explorer", path])
    else:
        print("🟡 Auto-open not supported on this OS.")

def reveal_in_file_manager(file_path):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.call(['open', '-R', file_path])
        elif system == "Windows":
            os.startfile(os.path.normpath(file_path))
        else:
            # For Linux or others, just open the folder
            folder = os.path.dirname(file_path)
            open_folder(folder)
    except Exception as e:
        print(f"Error opening file location: {e}")

class MainLayout(FloatLayout):
    light_theme = {
        'font_color': (0, 0, 0, 1),
        'background_color': (1, 1, 1, 1),
        'progress_color': (0.3, 0.6, 0.9, 1),
    }
    dark_theme = {
        'font_color': (1, 1, 1, 1),
        'background_color': (0.1, 0.1, 0.1, 1),
        'progress_color': (0.3, 0.6, 0.9, 1),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_mode = 'dark'

        self.label = Label(text="🎧 Drop audio files here to split them!",
                           font_name="DejaVuSans",
                           font_size=16,
                           size_hint=(None, None),
                           pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.add_widget(self.label)


        self.progress = ProgressBar(max=100, value=0,
                                    size_hint=(0.6, None), height=20,
                                    pos_hint={'center_x': 0.5, 'center_y': 0.4})
        self.add_widget(self.progress)

        self.output_layout = BoxLayout(orientation='vertical',
                                       size_hint=(1, 0.3),
                                       pos_hint={'center_x': 0.5, 'y': 0})
        self.add_widget(self.output_layout)

        self.theme_toggle_btn = Button(text="🌓 Theme",
                                    font_name="DejaVuSans",
                                      size_hint=(None, None),
                                      size=(80, 40),
                                      pos_hint={'center_x': 0.5, 'top': 0.98})
        self.theme_toggle_btn.bind(on_release=self._on_theme_toggle)
        self.add_widget(self.theme_toggle_btn)

        self.drag_overlay = FloatLayout(size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        with self.drag_overlay.canvas:
            Color(0, 0, 0, 0.2)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.drag_overlay.opacity = 0
        self.add_widget(self.drag_overlay)
        self.bind(size=self._update_rect, pos=self._update_rect)

        Window.bind(on_drop_file=self._on_file_drop)
        Window.bind(on_drag_enter=self._on_drag_enter)
        Window.bind(on_drag_leave=self._on_drag_leave)

        self.apply_theme()


    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _on_drag_enter(self, *args):
        self.drag_overlay.opacity = 1

    def _on_drag_leave(self, *args):
        self.drag_overlay.opacity = 0

    def apply_theme(self):
        theme = self.light_theme if self.theme_mode == 'light' else self.dark_theme
        font_color = theme['font_color']
        bg_color = theme['background_color']
        progress_color = theme['progress_color']

        self.label.color = font_color
        self.theme_toggle_btn.color = font_color
        self.progress.color = progress_color
        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

    def _update_bg_rect(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = self.size
            self.bg_rect.pos = self.pos

    def toggle_theme(self):
        self.theme_mode = 'light' if self.theme_mode == 'dark' else 'dark'
        self.apply_theme()

    def _on_file_drop(self, window, file_path, x, y, *args):
        file_path = file_path.decode("utf-8")
        self.drag_overlay.opacity = 0
        self.label.text = f"🎶 File received:\n{os.path.basename(file_path)}"
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.label.text += f"\nFile size: {file_size_mb:.2f}MB"

            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".wav":
                self.label.text += "\n🎼 Converting WAV to MP3..."
                file_path = convert_wav_to_mp3(file_path)
                self.label.text += "\n🎉 Conversion complete!"
            elif ext == ".m4a":
                self.label.text += "\n🎼 Converting WAV to MP3..."
                file_path = convert_m4a_to_mp3(file_path)
                self.label.text += "\n🎉 Conversion complete!"

            output_dir = os.path.dirname(file_path)
            output_files = []
            if file_size_mb > 8:
                self.label.text += "\n🔪 Splitting in progress..."
                Clock.schedule_interval(lambda dt: self.progress.setter('value')(self.progress, min(self.progress.value + 5, 100)), 0.1)
                output_files = split_mp3(file_path)
                Clock.schedule_once(lambda dt: self.progress.setter('value')(self.progress, 100), 1.2)
                self.label.text += f"\n✅ Split into {len(output_files)} parts!"
            else:
                output_files = [file_path]
                self.label.text += f"\n📦 Under 8MB. All good!"

            self._display_output_files(output_files)
            open_folder(output_dir)
        except Exception as e:
            self.label.text += f"\n❌ Error: {str(e)}"

    def _display_output_files(self, output_files):
        self.output_layout.clear_widgets()
        for file in output_files:
            btn = Button(text=os.path.basename(file), size_hint_y=None, height=40)
            def on_release_factory(f):
                def action(btn):
                    reveal_in_file_manager(f)
                    enable_drag_out(f)
                return action
            btn.bind(on_release=on_release_factory(file))
            self.output_layout.add_widget(btn)

    def _on_theme_toggle(self, instance):
        self.toggle_theme()

# --- Drag-out helper ---
def enable_drag_out(file_path):
    try:
        system = platform.system()
        if system == "Darwin":
            # macOS drag-out using pyobjc and NSPasteboard (placeholder logic)
            try:
                import AppKit
                pb = AppKit.NSPasteboard.generalPasteboard()
                pb.clearContents()
                pb.writeObjects_([AppKit.NSURL.fileURLWithPath_(file_path)])
                print("📤 Drag-ready on macOS.")
            except Exception as e:
                print(f"pyobjc not available or error: {e}")
        elif system == "Windows":
            # Windows drag-out using pywin32 (placeholder logic)
            try:
                import win32clipboard, win32con
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(file_path)
                win32clipboard.CloseClipboard()
                print("📤 Clipboard set for drag on Windows.")
            except Exception as e:
                print(f"pywin32 not available or error: {e}")
        else:
            print("⚠️ Drag-out not supported on this OS.")
    except Exception as e:
        print(f"Error preparing drag-out: {e}")

class EchoChefApp(App):
    def build(self):
        Window.size = (300, 400)
        return MainLayout()

if __name__ == '__main__':
    EchoChefApp().run()
