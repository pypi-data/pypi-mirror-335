import pyvisual as pv
from pyvisual.ui.inputs.pv_button import PvButton
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout


class PvGroup:
    def __init__(self, container=None, x=0, y=0, orientation="horizontal", spacing=10,
                 padding=(10, 10, 10, 10), background_color=(1, 1, 1, 0),
                 radius=0, border_color=(1, 0, 0, 1), border_width=1):
        self.container = container
        self.orientation = orientation
        self.spacing = spacing
        self.padding = padding
        self.background_color = background_color
        self.radius = radius
        self.border_color = border_color
        self.border_width = border_width
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.widgets = []  # Track all added widgets and groups
        # Create the container layout using Kivy's BoxLayout
        self.layout = BoxLayout(
            orientation=self.orientation,
            spacing=self.spacing,
            padding=self.padding,
            size_hint=(None, None),
            pos=(self.x, self.y)
        )
        # Custom background and border
        with self.layout.canvas.before:
            if self.background_color:
                Color(*self.background_color)
                self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[self.radius])

            if self.border_color and self.border_width > 0:
                Color(*self.border_color)
                self.border_line = Line(rounded_rectangle=(x, y, self.layout.size[0], self.layout.size[1], self.radius),
                                        width=self.border_width)

        # Add the layout to the container if a container is provided
        if self.container:
            self.container.add_widget(self.layout)
        self.layout.bind(size=self.update_background, pos=self.update_background)

    def add_widget(self, widget):
        """
        Add a widget or a list of widgets to the GroupLayout.
        """
        # Handle a list or single widget
        if isinstance(widget, (list, tuple)):
            for single_widget in widget:
                self._add_single_widget(single_widget)
        else:
            self._add_single_widget(widget)

        # Update layout size dynamically
        self.update_layout_size()
        self.update_background()

    def _add_single_widget(self, widget):
        """
        Add a single widget to the GroupLayout.
        """
        if isinstance(widget, (PvGroup,pv.PvScroll)):
            self.widgets.append(widget)  # Track the nested group
            self.layout.add_widget(widget.layout)  # Add the nested layout
        else:
            self.widgets.append(widget)
            self.layout.add_widget(widget)
    def update_layout_size(self):
        """
        Calculate and adjust layout size based on children, accounting for nested groups as single entities.
        """
        total_width = self.padding[0] + self.padding[2]
        total_height = self.padding[1] + self.padding[3]


        if len(self.widgets) > 0:
            if self.orientation == "horizontal":
                # Sum the widths of all children or nested groups
                total_width += sum(
                    child.layout.size[0] if isinstance(child, (PvGroup,pv.PvScroll)) else child.width
                    for child in self.widgets
                )
                # Add spacing between children
                total_width += (len(self.widgets) - 1) * self.spacing
                # Height is the max height of any child or nested group
                total_height += max(
                    child.layout.size[1] if isinstance(child, (PvGroup,pv.PvScroll)) else child.height
                    for child in self.widgets
                )
            else:  # Vertical orientation
                # Width is the max width of any child or nested group
                total_width += max(
                    child.layout.size[0] if isinstance(child, (PvGroup,pv.PvScroll)) else child.width
                    for child in self.widgets
                )
                # Sum the heights of all children or nested groups
                total_height += sum(
                    child.layout.size[1] if isinstance(child, (PvGroup,pv.PvScroll)) else child.height
                    for child in self.widgets
                )
                # Add spacing between children
                total_height += (len(self.widgets) - 1) * self.spacing

        # Update the layout size
        self.layout.size = (total_width, total_height)
        self.width = total_width
        self.height = total_height
        print(total_width,total_height)
        self.update_background()

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
        self.widgets.clear()
        self.layout.clear_widgets()
        self.update_layout_size()
        self.update_background()

    def remove_widget(self, index):
        """
        Remove a specific widget by index from the GroupLayout.
        """
        try:
            widget = self.widgets[index]
            self.widgets.remove(widget)
            self.layout.remove_widget(widget.layout if isinstance(widget, (PvGroup,pv.PvScroll) ) else widget)
            self.update_layout_size()
            self.update_background()
        except IndexError:
            print(f"Invalid index: {index}. No widget removed.")


if __name__ == '__main__':
    import pyvisual as pv

    window = pv.PvWindow()

    # Main Vertical Group
    vertical_group = PvGroup(
        container=window, x=50, y=200, orientation="vertical", spacing=20,
        padding=(30, 30, 30, 30), background_color=(0.9, 0.9, 0.9, 1),
        radius=5, border_color=(0.3, 0.3, 0.3, 1), border_width=1
    )

    # Nested Horizontal Group
    horizontal_group = PvGroup(
        orientation="horizontal", spacing=15, padding=(10, 10, 10, 10),
        background_color=(0.8, 0.8, 0.8, 1), radius=5, border_color=(0, 0, 1, 1), border_width=1
    )

    # Add buttons to the horizontal group
    button1 = pv.PvButton(None, text="Button 1")
    button2 = pv.PvButton(None, text="Button 2")
    horizontal_group.add_widget(button1)
    horizontal_group.add_widget(button2)

    # Add the horizontal group to the vertical group
    vertical_group.add_widget(horizontal_group)

    # Add a button directly to the vertical group
    vertical_group.add_widget(pv.PvButton(None, text="Button 3"))

    # Check the size of the vertical group
    print(f"Vertical Group Size: {vertical_group.layout.size}")

    # Show the window
    window.show()
