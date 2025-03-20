from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line


class BasicToggleButton(Widget):
    def __init__(self, window, x, y, width=60, height=30, padding=4,
                 on_color=(0.3, 0.8, 0.3, 1), off_color=(0.8, 0.3, 0.3, 1),
                 border_color=(0.3, 0.3, 0.3, 1), border_thickness=1,
                 switch_color=(1, 1, 1, 1), is_on=False,
                 toggle_callback=None):
        super().__init__()

        # Store properties
        self.size_hint = (None, None)
        self.size = (width, height)  # Size of the toggle button
        self.is_on = is_on
        self.on_color = on_color
        self.off_color = off_color
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.switch_color = switch_color
        self.toggle_callback = toggle_callback
        self.padding = padding  # Padding around the switch

        # Set widget position
        self.pos = (x, y)

        # Calculate switch size and initial position
        switch_size = (self.size[1] - 2 * self.padding, self.size[1] - 2 * self.padding)
        if self.is_on:
            switch_x = self.pos[0] + self.size[0] - self.padding - switch_size[0]
        else:
            switch_x = self.pos[0] + self.padding
        switch_y = self.pos[1] + self.padding
        self.switch_pos = (switch_x, switch_y)

        # Draw the toggle button with background, border, and switch
        with self.canvas:
            # Draw the background rectangle based on the state
            self.bg_color_instruction = Color(*self.on_color if self.is_on else self.off_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

            # Draw the border around the toggle button
            Color(*self.border_color)
            self.border = Line(rectangle=(self.pos[0], self.pos[1],
                                         self.size[0], self.size[1]),
                               width=self.border_thickness)

            # Draw the switch
            Color(*self.switch_color)
            self.switch = Rectangle(pos=self.switch_pos, size=switch_size)

        # Bind to position and size changes if necessary
        self.bind(pos=self.update_toggle_graphics, size=self.update_toggle_graphics)

        # Add the toggle button widget to the window
        window.add_widget(self)

    def on_touch_down(self, touch):
        """Toggle the button state on click."""
        if self.collide_point(*touch.pos):
            self.is_on = not self.is_on
            self.update_toggle_appearance()

            # Trigger callback if provided
            if self.toggle_callback:
                self.toggle_callback(self)
            return True
        return False

    def update_toggle_appearance(self):
        """Update the toggle button appearance based on the state."""
        # Update background color
        self.bg_color_instruction.rgba = self.on_color if self.is_on else self.off_color

        # Update switch position
        self.update_switch_position()

    def update_switch_position(self):
        """Move the switch to the appropriate position based on the state."""
        # Determine new switch position
        if self.is_on:
            new_x = self.pos[0] + self.size[0] - self.padding - self.switch.size[0]
        else:
            new_x = self.pos[0] + self.padding

        # Update the switch position
        self.switch.pos = (new_x, self.pos[1] + self.padding)

    def update_toggle_graphics(self, *args):
        """Update the position and size of the background, border, and switch when the widget properties change."""
        # Update background rectangle
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        # Update border
        self.canvas.remove(self.border)
        with self.canvas:
            Color(*self.border_color)
            self.border = Line(rectangle=(self.pos[0], self.pos[1],
                                         self.size[0], self.size[1]),
                               width=self.border_thickness)

        # Update switch size
        switch_size = (self.size[1] - 2 * self.padding, self.size[1] - 2 * self.padding)
        self.switch.size = switch_size

        # Update switch position based on state
        self.update_switch_position()

    def set_border(self, border_color, border_thickness):
        """Set the border color and thickness."""
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.update_toggle_graphics()

    def set_padding(self, padding):
        """Set the padding and update the toggle button appearance."""
        self.padding = padding
        self.update_toggle_graphics()

    def set_switch_color(self, switch_color):
        """Set the switch color."""
        self.switch_color = switch_color
        self.switch.color = self.switch_color
        self.update_toggle_graphics()


# Example usage of the BasicCheckbox and BasicToggleButton classes
if __name__ == "__main__":
    import pyvisual as pv
    window = pv.Window()
    # Toggle callback function for checkbox
    def on_checkbox_toggle(cb):
        print(f"Checkbox State: {'Checked' if cb.is_checked else 'Unchecked'}")

    # Toggle callback function for toggle button
    def on_toggle_button_toggle(tb):
        print(f"Toggle Button State: {'On' if tb.is_on else 'Off'}")


    # Add a basic toggle button
    custom_toggle_button = BasicToggleButton(
        window=window,
        x=200, y=300,
        width=60, height=30,
        padding=4,  # Adjust padding here
        on_color=(0.3, 0.8, 0.3, 1),  # Green when on
        off_color=(0.8, 0.3, 0.3, 1),  # Red when off
        border_color=(0.3, 0.3, 0.3, 1),
        border_thickness=1,
        switch_color=(1, 1, 1, 1),  # White switch
        is_on=False,
        toggle_callback=on_toggle_button_toggle
    )

    # Optionally, add another toggle button with different properties
    custom_toggle_button2 = BasicToggleButton(
        window=window,
        x=200, y=250,
        width=80, height=40,
        padding=6,
        on_color=(0.2, 0.6, 1, 1),  # Blue when on
        off_color=(1, 0.6, 0.2, 1),  # Orange when off
        border_color=(0.2, 0.2, 0.2, 1),
        border_thickness=2,
        switch_color=(1, 1, 1, 1),
        is_on=True,
        toggle_callback=lambda tb: print(f"Toggle Button 2 State: {'On' if tb.is_on else 'Off'}")
    )

    # Display the window with the added widgets
    window.show()
