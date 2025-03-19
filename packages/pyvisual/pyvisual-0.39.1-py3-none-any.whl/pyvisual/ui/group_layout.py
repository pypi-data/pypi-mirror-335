import pyvisual as pv
from pyvisual.ui.input.pv_button import BasicButton
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout


class GroupLayout:
    def __init__(self, window=None, x=0, y=0, orientation="horizontal", spacing=10,
                 padding=(10, 10, 10, 10), background_color=(1, 1, 1, 0),
                 radius=0, border_color=(1, 0, 0, 1), border_width=1):
        self.window = window
        self.orientation = orientation
        self.spacing = spacing
        self.padding = padding
        self.background_color = background_color
        self.radius = radius
        self.border_color = border_color
        self.border_width = border_width

        # Create the container layout using Kivy's BoxLayout
        self.layout = BoxLayout(
            orientation=self.orientation,
            spacing=self.spacing,
            padding=self.padding,
            size_hint=(None, None),
            pos=(x, y)
        )
        # Custom background and border
        with self.layout.canvas.before:
            if self.background_color:
                Color(*self.background_color)
                self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[self.radius])

            if self.border_color and self.border_width > 0:
                Color(*self.border_color)
                self.border_line = Line(rounded_rectangle=(x, y, self.layout.size[0], self.layout.size[1], self.radius), width=self.border_width)

        # Bind size updates

        # Add the layout to the window if a window is provided
        if self.window:
            self.window.add_widget(self.layout)
        self.layout.bind(size=self.update_background, pos=self.update_background)


    def add_widget(self, widget):
        """
        Add a widget to the GroupLayout.
        """
        if isinstance(widget, GroupLayout):
            self.layout.add_widget(widget.layout)  # Add nested layout
        else:
            my_widget = widget if isinstance(widget, BasicButton) else widget

            if my_widget.parent is not None:
                my_widget.parent.remove_widget(my_widget)
            self.layout.add_widget(my_widget)

        # Update layout size dynamically
        self.update_layout_size()

        self.update_background()

    def update_layout_size(self):
        """
        Calculate and adjust layout size based on children.
        """
        if len(self.layout.children) == 0:
            total_width = self.padding[0] + self.padding[2]
            total_height = self.padding[1] + self.padding[3]
        elif self.orientation == "horizontal":
            total_width = (
                    sum(child.width for child in self.layout.children) +
                    (len(self.layout.children) - 1) * self.spacing +
                    self.padding[0] + self.padding[2]
            )
            total_height = (
                    max(child.height for child in self.layout.children) +
                    self.padding[1] + self.padding[3]
            )
        else:  # Vertical orientation
            total_width = (
                    max(child.width for child in self.layout.children) +
                    self.padding[0] + self.padding[2]
            )
            total_height = (
                    sum(child.height for child in self.layout.children) +
                    (len(self.layout.children) - 1) * self.spacing +
                    self.padding[1] + self.padding[3]
            )

        # Adjust the position to grow downward if vertical
        if self.orientation == "vertical":
            self.layout.pos = (self.layout.pos[0], self.layout.pos[1] - (total_height - self.layout.height))

        self.layout.size = (total_width, total_height)

    def update_background(self, *args):
        """
        Update the background and border on size changes.
        """
        if self.background_color:
            self.bg_rect.size = self.layout.size
            self.bg_rect.pos = self.layout.pos
            self.bg_rect.radius = [self.radius]

        if self.border_color and self.border_width > 0:
            self.border_line.rounded_rectangle = (
                self.layout.x, self.layout.y, self.layout.width, self.layout.height, self.radius
            )

    def clear_widgets(self):
        """
        Remove all widgets from the GroupLayout.
        """
        self.layout.clear_widgets()
        self.update_layout_size()
        self.update_background()

    def remove_widget(self, index):
        """
        Remove a specific widget by index from the GroupLayout.
        """
        try:
            widget = self.layout.children[::-1][index]  # Access widget by index in reversed order
            self.layout.remove_widget(widget)
            self.update_layout_size()
            self.update_background()
        except IndexError:
            print(f"Invalid index: {index}. No widget removed.")


# Example Usage
if __name__ == "__main__":
    # Initialize the pyvisual window
    window = pv.Window(title="Nested GroupLayout Example")

    # Main Horizontal GroupLayout
    vertical_group = GroupLayout(
        window=window, x=50, y=200, orientation="vertical", spacing=20,
        padding=(30, 30, 30, 30), background_color=(0.9, 0.9, 0.9, 1),
        radius=5, border_color=(0.3, 0.3, 0.3, 1), border_width=0
    )

    pv.BasicButton(vertical_group,x=100,y=100)
    button2 = pv.BasicButton(None, x=100, y=100,text="Dont Click Me ")
    button2.add_to_layout(vertical_group)
    button3 = pv.BasicButton(None, x=100, y=100,text="Dont Click ")
    vertical_group.add_widget(button3)
    pv.Text(vertical_group)

    # vertical_group.clear_widgets()

    # vertical_group.remove_widget()





    # Show the window
    window.show()
