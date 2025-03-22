from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color


class RectangleShape(Widget):
    def __init__(self, window, x, y, width, height, color=(1, 1, 1, 1), visibility=True, tag=None):
        super().__init__(size_hint=(None, None), pos=(x, y))

        self.width = width
        self.height = height
        self.color = color
        self.tag = tag
        self.visibility = visibility

        # Add the rectangle to the canvas
        with self.canvas:
            self.color_instruction = Color(*self.color)  # RGBA color
            self.rectangle = Rectangle(size=(self.width, self.height), pos=self.pos)

        # Set initial visibility
        self.set_visibility(self.visibility)

        # Add the widget to the window
        window.add_widget(self)

    def set_size(self, width, height):
        """Update the size of the rectangle."""
        self.width = width
        self.height = height
        self.rectangle.size = (self.width, self.height)

    def set_position(self, x, y):
        """Update the position of the rectangle."""
        self.pos = (x, y)
        self.rectangle.pos = self.pos

    def set_color(self, color):
        """Update the color of the rectangle."""
        self.color = color
        self.color_instruction.rgba = self.color

    def set_visibility(self, visibility):
        """Show or hide the rectangle."""
        if visibility:
            self.opacity = 1
            self.canvas.opacity = 1
        else:
            self.opacity = 0
            self.canvas.opacity = 0

        self.visibility = visibility


if __name__ == "__main__":
    import pyvisual as pv

    window = pv.Window()
    # Create a button with various text styles
    button = RectangleShape(window, 0, 0, 100, 300,
                            color=(0, 1, 1, 1), visibility=True, tag=None)

    window.show()
