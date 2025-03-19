from kivy.uix.label import Label
from kivy.core.text import LabelBase


class Text(Label):
    def __init__(self, window, x, y, text="Hello",
                 font=None, font_size=20, font_color=(0.3, 0.3, 0.3, 1),
                 bold=False, italic=False, underline=False, strikethrough=False, hidden=False,tag= None):
        # Initialize the main text label with basic properties
        super().__init__(
            size_hint=(None, None),  # Disable size hint
            halign='left',
            valign='bottom',
            text_size=(None, None),  # Disable automatic wrapping or sizing
        )

        # Store the initial position as the anchor point (bottom-left)
        self.anchor_x = x
        self.anchor_y = y  # This is the bottom-left corner position

        # Store reference to the window
        self.window = window

        # Enable markup to use BBCode-like tags
        self.markup = True
        self.tag = tag

        # Store style properties
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough

        # Store initial text without markup
        self.raw_text = text

        # Apply the text with markup
        self.text = self.apply_markup(text)

        # Register custom font if provided
        if font and font.endswith((".ttf", ".otf")):
            LabelBase.register(name="CustomFont", fn_regular=font)
            self.font_name = "CustomFont"
        else:
            self.font_name = "Roboto"  # Default font

        # Set font properties
        self.font_size = font_size
        self.color = font_color

        # Bind the on_font_size method to handle font size changes
        self.bind(font_size=self.on_font_size)

        # Update texture and size
        self.texture_update()
        self.size = self.texture_size

        # Adjust position to keep bottom-left corner at (x, y)
        self.update_position()

        self.hidden = hidden  # Initialize hidden state
        # Add the image to the window if not hidden
        if not self.hidden:
            window.add_widget(self)


    def apply_markup(self, text):
            """Apply markup tags to the text based on style properties."""
            # Start with the raw text
            styled_text = text

            # Apply tags in the correct order
            if self.strikethrough:
                styled_text = f"[s]{styled_text}[/s]"
            if self.underline:
                styled_text = f"[u]{styled_text}[/u]"
            if self.italic:
                styled_text = f"[i]{styled_text}[/i]"
            if self.bold:
                styled_text = f"[b]{styled_text}[/b]"

            return styled_text

    def on_font_size(self, instance, value):
        """Automatically called when font_size changes."""
        self.texture_update()
        self.size = self.texture_size
        self.update_position()

    def update_position(self):
        """Adjust the position of the text to keep the anchor point fixed (bottom-left)."""
        # Calculate offsets dynamically based on the font size
        x_offset = self.font_size * (-9 / 100)  # Scale the x offset based on font size
        y_offset = self.font_size * (-25 / 100)  # Scale the y offset based on font size

        # Update texture and size
        self.texture_update()
        self.size = self.texture_size

        # Position the text based on the bottom-left origin with calculated offsets
        self.x = self.anchor_x + x_offset
        self.y = self.anchor_y + y_offset

    def set_position(self, x, y):
        """Update the anchor position of the text."""
        self.anchor_x = x
        self.anchor_y = y
        self.update_position()

    def set_text(self, text):
        """Update the text content."""
        self.raw_text = text
        self.text = self.apply_markup(text)
        self.texture_update()
        self.size = self.texture_size

        # Update position after text change
        self.update_position()

    def set_font(self, font):
        """Set a new font for the text."""
        if font and font.endswith((".ttf", ".otf")):
            LabelBase.register(name="CustomFont", fn_regular=font)
            self.font_name = "CustomFont"
        else:
            self.font_name = font

        self.texture_update()
        self.size = self.texture_size

        # Update position after font change
        self.update_position()

    def set_color(self, color):
        """Set the color of the text."""
        self.color = color

    def set_font_size(self, font_size):
        """Set a new font size for the text."""
        self.font_size = font_size
        # The on_font_size method will be called automatically

    def set_bold(self, bold):
        """Set the bold style."""
        self.bold = bold
        self.text = self.apply_markup(self.raw_text)
        self.texture_update()
        self.size = self.texture_size
        self.update_position()

    def set_italic(self, italic):
        """Set the italic style."""
        self.italic = italic
        self.text = self.apply_markup(self.raw_text)
        self.texture_update()
        self.size = self.texture_size
        self.update_position()

    def set_underline(self, underline):
        """Set the underline style."""
        self.underline = underline
        self.text = self.apply_markup(self.raw_text)
        self.texture_update()
        self.size = self.texture_size
        self.update_position()

    def set_strikethrough(self, strikethrough):
        """Set the strikethrough style."""
        self.strikethrough = strikethrough
        self.text = self.apply_markup(self.raw_text)
        self.texture_update()
        self.size = self.texture_size
        self.update_position()

    def destroy(self):
        """Remove the text widget from the window."""
        # Check if the widget is still part of the window
        if self.window and self in self.window.children:
            self.window.remove_widget(self)

    def set_hidden(self, hidden):
        """Show or hide the image."""
        if hidden and not self.hidden:
            self.parent.remove_widget(self)  # Remove image from window if hidden
        elif not hidden and self.hidden:
            self.parent.add_widget(self)  # Add image back to window if shown
        self.hidden = hidden


if __name__ == "__main__":
    import pyvisual as pv

    window = pv.Window()

    # Add a text element to the window with dynamic offset calculation
    text_label_large = Text(
        window=window,
        x=0, y=0,  # Position of the text (bottom-left)
        text="Hello World",
        font="Roboto",
        font_size="20sp",  # Initial large font size
        font_color=(0.3, 0.3, 0.3, 1),  # Text color
    )

    # Show the window
    window.show()
