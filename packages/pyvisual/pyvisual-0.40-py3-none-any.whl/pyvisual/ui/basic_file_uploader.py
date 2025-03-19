from kivy.uix.button import Button as KivyButton
from kivy.graphics import Line, Color
from kivy.core.window import Window as KivyWindow
from kivy.core.text import LabelBase
import tkinter as tk
from tkinter import filedialog
import threading

class FileUploader:
    def __init__(self, window, x, y, width=140, height=50, text="UPLOAD FILE",
                 idle_color=(1, 1, 1, 1), hover_color=(0.7, 0.7, 0.7, 1), text_color=(0.6, 0.6, 0.6, 1),
                 border_color=(0, 0, 0, 1), border_thickness=1,
                 on_file_selected=None, on_cancel=None,
                 font="Roboto", font_size=16):
        """
        Initialize the FileUploader button.

        :param window: The pyvisual.Window instance to add the uploader to.
        :param x: X position of the button.
        :param y: Y position of the button.
        :param width: Width of the button.
        :param height: Height of the button.
        :param text: Text displayed on the button.
        :param idle_color: Background color when idle.
        :param hover_color: Background color when hovered.
        :param text_color: Color of the text.
        :param border_color: Color of the border.
        :param border_thickness: Thickness of the border.
        :param on_file_selected: Callback function when a file is selected.
        :param on_cancel: Callback function when the dialog is canceled.
        :param font: Font name or file path.
        :param font_size: Size of the font.
        """
        # Initialize properties
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.font_size = font_size
        self.on_file_selected = on_file_selected
        self.on_cancel = on_cancel

        # Register font if a file path is provided
        if font.endswith((".ttf", ".otf")):
            LabelBase.register(name="CustomFont", fn_regular=font)
            self.font_name = "CustomFont"
        else:
            self.font_name = font

        # Create the main button widget
        self.button_widget = KivyButton(
            text=self.text,
            size=(self.width, self.height),
            pos=(self.x, self.y),
            background_normal='',  # Disable default background
            background_color=self.idle_color,
            color=self.text_color,
            font_name=self.font_name,
            font_size=self.font_size,
            size_hint=(None, None)
        )

        # Draw the custom border
        self.draw_border()

        # Bind button click to open file dialog
        self.button_widget.bind(on_press=self.open_file_dialog)

        # Monitor mouse position for hover effect
        KivyWindow.bind(mouse_pos=self.on_mouse_pos)

        # Add the button to the window
        window.add_widget(self.button_widget)

    def draw_border(self):
        """Draw a custom border around the button."""
        with self.button_widget.canvas.before:
            Color(*self.border_color)
            self.border_line = Line(
                rectangle=(self.button_widget.x, self.button_widget.y,
                           self.button_widget.width, self.button_widget.height),
                width=self.border_thickness
            )
        # Bind to position and size changes to update the border
        self.button_widget.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        """Update the border line when the button's position or size changes."""
        self.border_line.rectangle = (self.button_widget.x, self.button_widget.y,
                                      self.button_widget.width, self.button_widget.height)

    def on_mouse_pos(self, window, pos):
        """Detect hover by checking if the mouse is within the button area."""
        if self.is_mouse_hovering(pos):
            self.button_widget.background_color = self.hover_color
        else:
            self.button_widget.background_color = self.idle_color

    def is_mouse_hovering(self, pos):
        """Check if the mouse is within the button's boundaries."""
        return (self.button_widget.x <= pos[0] <= self.button_widget.x + self.button_widget.width and
                self.button_widget.y <= pos[1] <= self.button_widget.y + self.button_widget.height)

    def open_file_dialog(self, instance):
        """Open the native OS file chooser dialog in a separate thread."""
        thread = threading.Thread(target=self._open_file_dialog_thread)
        thread.start()

    def _open_file_dialog_thread(self):
        """Thread target to open the file dialog."""
        # Initialize Tkinter and hide the main window
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        try:
            # Open the file dialog
            file_path = filedialog.askopenfilename(title="Select a File")

            if file_path:
                if self.on_file_selected:
                    # Ensure the callback is called in the main thread
                    KivyWindow.bind(on_draw=lambda *args: self.on_file_selected(file_path))
            else:
                if self.on_cancel:
                    # Ensure the callback is called in the main thread
                    KivyWindow.bind(on_draw=lambda *args: self.on_cancel())
        finally:
            root.destroy()  # Destroy the Tkinter root window

    def set_border(self, border_thickness, border_color):
        """Set the border thickness and color, and redraw the border."""
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.button_widget.canvas.before.clear()  # Clear the previous canvas
        self.draw_border()  # Redraw the border with new settings

    def set_font(self, font_name, font_size):
        """Set the font name or file path and font size."""
        if font_name.endswith((".ttf", ".otf")):
            LabelBase.register(name="CustomFont", fn_regular=font_name)
            self.button_widget.font_name = "CustomFont"
        else:
            self.button_widget.font_name = font_name
        self.button_widget.font_size = font_size


if __name__ == "__main__":

    import pyvisual as pv
    window = pv.Window()
    def on_file_selected(file_path):
        print(f"Selected file: {file_path}")

    def on_cancel():
        print("File selection canceled.")

    # Create a file uploader with callbacks
    uploader = FileUploader(
        window=window,
        x=325, y=275,
        width=150, height=50,
        text="Upload File",
        idle_color=(0.2, 0.6, 0.86, 1),  # Blue for idle state
        hover_color=(0.1, 0.5, 0.76, 1),  # Darker Blue for hover state
        text_color=(1, 1, 1, 1),  # White Text Color
        border_color=(0, 0, 0, 1),  # Border Color
        border_thickness=2,  # Border thickness
        on_file_selected=on_file_selected,
        on_cancel=on_cancel,
        font="Roboto",
        font_size=16
    )

    window.show()
