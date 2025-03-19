from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Line, Rectangle


class BasicTextInput(Widget):
    def __init__(self, window, x, y, width=200, height=40, background_color=(1, 1, 1, 1), input_type="text", visibility=True,
                 placeholder="Enter your text here...", default_text="",
                 text_padding_left=10, text_padding_right=10, text_padding_top=0, text_padding_bottom=10,
                 font="Roboto", font_size=None, font_color=(0.3, 0.3, 0.3, 1),
                 border_color=(0.6, 0.6, 0.6, 1), border_thickness=1, border_style=("bottom", "top", "right", "left"),
                 on_input=None, tag=None, disabled=False, disabled_opacity=0.5):
        super().__init__()

        # Store padding values and border style
        self.text_padding_left = text_padding_left
        self.text_padding_right = text_padding_right
        self.text_padding_top = text_padding_top
        self.text_padding_bottom = text_padding_bottom
        self.border_style = border_style
        self.tag = tag
        self.disabled = disabled  # Initialize disabled state
        self.disabled_opacity = disabled_opacity

        # Calculate the font size based on the height if not specified
        if not font_size:
            # Calculate the available height by subtracting top and bottom padding
            available_height = height - text_padding_top - text_padding_bottom
            self.font_size = available_height * 0.6  # Use 60% of the available height for font size
        else:
            self.font_size = font_size

        # Set widget properties
        self.size_hint = (None, None)
        self.size = (width, height)
        self.pos = (x, y)

        # Create the TextInput as an internal widget with placeholder and default text
        self.text_input = TextInput(
            size_hint=(None, None),
            size=(width - border_thickness * 2, height - border_thickness * 2),
            pos=(x + border_thickness, y + border_thickness),
            font_size=self.font_size,
            font_name=font,
            foreground_color=font_color,
            cursor_color=(0, 0, 0, 1),
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            multiline=False,
            hint_text=placeholder,
            hint_text_color=(0.7, 0.7, 0.7, 1),
            text=default_text,
            password=input_type == "password",
            padding=[self.text_padding_left, self.text_padding_bottom, self.text_padding_right, self.text_padding_top],
            disabled=disabled
        )

        # Apply input restrictions based on the `input_type`
        self.apply_input_restrictions(input_type)

        # If a text callback is provided, bind it
        if on_input:
            self.text_input.bind(text=on_input)

        # Draw the background of the text box using canvas
        with self.canvas:
            Color(*background_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        # Draw the border or lines based on the `border_style`
        self.update_border_style(border_color, border_thickness)

        # Add the internal TextInput to the parent widget (BasicTextInput)
        self.add_widget(self.text_input)

        # Update the border and rectangle on position and size change
        self.bind(pos=self.update_graphics, size=self.update_graphics)

        # Add the BasicTextInput to the main window
        window.add_widget(self)

        self.visibility = visibility
        self.set_visibility(self.visibility)
        self.set_disabled(self.disabled)

    def apply_input_restrictions(self, input_type):
        """Apply input restrictions based on the input type."""
        if input_type == "number":
            self.text_input.input_filter = 'int'
        elif input_type == "float":
            self.text_input.input_filter = 'float'
        elif input_type == "email":
            self.text_input.input_filter = lambda text, from_undo: text.replace(" ", "")
        elif input_type == "alphabet":
            self.text_input.input_filter = lambda text, from_undo: "".join([c for c in text if c.isalpha()])
        else:
            self.text_input.input_filter = None

    def update_border_style(self, border_color, border_thickness):
        """Draw the borders based on the specified style."""
        with self.canvas:
            Color(*border_color)
            # Draw borders based on `border_style`
            if "top" in self.border_style:
                self.top_line = Line(points=[self.x, self.top, self.x + self.width, self.top], width=border_thickness)
            if "bottom" in self.border_style:
                self.bottom_line = Line(points=[self.x, self.y, self.x + self.width, self.y], width=border_thickness)
            if "left" in self.border_style:
                self.left_line = Line(points=[self.x, self.y, self.x, self.top], width=border_thickness)
            if "right" in self.border_style:
                self.right_line = Line(points=[self.right, self.y, self.right, self.top], width=border_thickness)

    def update_graphics(self, *args):
        """Update the canvas rectangle and borders when the widget size or position changes."""
        # Update background rectangle
        self.rect.pos = self.pos
        self.rect.size = self.size

        # Update border lines dynamically based on position and size
        if hasattr(self, 'top_line'):
            self.top_line.points = [self.x, self.top, self.x + self.width, self.top]
        if hasattr(self, 'bottom_line'):
            self.bottom_line.points = [self.x, self.y, self.x + self.width, self.y]
        if hasattr(self, 'left_line'):
            self.left_line.points = [self.x, self.y, self.x, self.top]
        if hasattr(self, 'right_line'):
            self.right_line.points = [self.right, self.y, self.right, self.top]

    def get_text(self):
        """Get the current text value from the internal TextInput."""
        return self.text_input.text

    def set_text(self, value):
        """Set the text value of the internal TextInput."""
        self.text_input.text = value

    def set_cursor_position(self, position):
        """Set the cursor position to the specified index in the text."""
        if 0 <= position <= len(self.text_input.text):
            self.text_input.cursor = (position, 0)  # (column, row)
        else:
            raise ValueError(
                f"Cursor position {position} is out of range for the current text length {len(self.text_input.text)}.")

    def set_visibility(self, visibility):
        """Show or hide the line."""
        if visibility:
            self.opacity = self.disabled_opacity if self.disabled else 1
            self.canvas.opacity = self.opacity
        else:
            self.opacity = 0
            self.canvas.opacity = 0

        self.visibility = visibility

    def set_disabled(self, disabled):
        """Enable or disable the text input."""
        self.disabled = disabled
        self.text_input.disabled = disabled
        self.opacity = self.disabled_opacity if self.disabled else 1


# Example usage of the BasicTextInput class
if __name__ == "__main__":
    import pyvisual as pv
    window = pv.Window()

    # Create an instance of BasicTextInput with adjusted settings
    text_input_default = BasicTextInput(
        window=window,
        x=100, y=300,  # Position
        width=400,
        height=50,  # Adjust height
        disabled=False,
    )

    # Display the window
    window.show()
