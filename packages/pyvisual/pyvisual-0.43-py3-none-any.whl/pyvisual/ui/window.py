import os
import sys
import logging

# Configure logging
from kivy.logger import Logger

# Remove all existing handlers
for handler in Logger.handlers[:]:
    Logger.removeHandler(handler)

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)

# Add the console handler to Kivy's logger
Logger.addHandler(console_handler)
Logger.setLevel(logging.WARNING)

from kivy.config import Config
from kivy.core.window import Window as KivyWindow
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
import platform

# DPI Awareness and Scaling Detection for Windows
scaling_factor = 1.0  # Default scaling factor is 1.0 (no scaling)

if platform.system() == "Windows":
    import ctypes

    try:
        ctypes.windll.user32.SetProcessDPIAware()
        user32 = ctypes.windll.user32
        dpi = user32.GetDpiForWindow(user32.GetForegroundWindow())
        scaling_factor = dpi / 96.0
    except Exception as e:
        print(f"Unable to set DPI awareness or detect scaling factor: {e}")

# Calculate the adjusted window size based on scaling
base_width, base_height = 800, 600
adjusted_width = int(base_width / scaling_factor)
adjusted_height = int(base_height / scaling_factor)

# Ensure Kivy respects the exact size configuration
Config.set('graphics', 'width', str(adjusted_width))
Config.set('graphics', 'height', str(adjusted_height))
Config.set('graphics', 'borderless', '0')  # Enable border for accurate dimensions
Config.set('graphics', 'fullscreen', '0')  # Disable fullscreen to maintain window size
Config.write()

class Window:
    def __init__(self, title="PyVisual Window", width=800, height=600, bg_color=(1, 1, 1, 1),
                 icon=None, bg_image=None, is_frameless=False, is_resizable=False):
        # Set a default icon path if none is provided
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.default_icon_path = os.path.join(base_path, "assets", "icons", "window", "window.png")

        # Adjust window size according to detected scaling factor
        self.title = title
        self.width = width
        self.height = height
        self.size = (int(self.width / scaling_factor), int(self.height / scaling_factor))
        self.bg_color = bg_color
        self.is_frameless = is_frameless
        self.is_resizable = is_resizable
        self.bg_image = bg_image
        self.icon_path = icon or self.default_icon_path

        # Set window properties using Kivy
        self._configure_window()

        # Root widget container
        self.root_widget = FloatLayout(size=self.size)

        if self.bg_image:
            self.set_bg_image(self.bg_image)

        # Bind resize event if is_resizable is True
        if self.is_resizable:
            KivyWindow.bind(on_resize=self.on_window_resize)
        else:
            KivyWindow.unbind(on_resize=self.on_window_resize)

    def _configure_window(self):
        """Apply window configuration settings."""
        Config.set('graphics', 'width', str(self.size[0]))
        Config.set('graphics', 'height', str(self.size[1]))
        Config.set('graphics', 'borderless', str(int(self.is_frameless)))
        Config.set('graphics', 'is_resizable', str(int(self.is_resizable)))
        Config.write()

        # Apply settings directly to the Kivy window
        KivyWindow.size = self.size
        KivyWindow.clearcolor = self.bg_color
        KivyWindow.borderless = self.is_frameless
        KivyWindow.fullscreen = False
        KivyWindow.is_resizable = self.is_resizable

        # Set the icon
        KivyWindow.set_icon(self.icon_path)

    def set_borderless(self, borderless):
        """Set the borderless property of the window."""
        self.borderless = borderless
        KivyWindow.borderless = self.borderless

    def set_bg_image(self, bg_image):
        """Add a background image to the window and ensure it fills the window."""
        self.bg_image = KivyImage(source=bg_image)

        # self.bg_image.pos = (100, 100)
        # self.bg_image.size = 20,20
        self.bg_image.fit_mode = "cover"
        self.root_widget.add_widget(self.bg_image, index=0)


    def on_window_resize(self, instance, width, height):
        """Adjust the background image on window resize."""
        self.size = (width, height)
        if hasattr(self, 'bg_image'):
            self.bg_image.size = (width, height)

    def add_widget(self, widget):
        """Add a widget to the window's main container."""
        self.root_widget.add_widget(widget)

    def show(self):
        """Show the window by running the Kivy app."""

        class PyVisualApplication(App):
            def build(self):
                return self.root_widget

            def on_start(self):
                KivyWindow.set_title(self.get_application_name())

            def get_application_name(self):
                return self.title

        app = PyVisualApplication()
        app.root_widget = self.root_widget
        app.title = self.title
        self.app = app  # Store reference to the app instance
        app.run()

    def close(self):
        """Close the window and exit the application."""
        self.app.stop()

    def update(self):
        """Force a refresh of the window."""
        # This method can include logic to force a re-draw or re-layout
        if self.root_widget:
            self.root_widget.canvas.ask_update()

if __name__ == "__main__":
    window = Window(
        title="PyVisual Window",
        width=800, height=600,
        bg_color=(1, 1, 1, 1),
        is_frameless=False,
    )
    # Set the window to borderless
    # window.set_borderless(True)
    window.show()
