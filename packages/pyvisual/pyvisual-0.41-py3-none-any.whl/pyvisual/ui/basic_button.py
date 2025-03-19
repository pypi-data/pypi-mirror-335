from kivy.graphics import BoxShadow, Color, RoundedRectangle, Line
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.core.window import Window as KivyWindow

class BasicButton(Widget):
    def __init__(self, window, x, y,
                 width=140, height=50, text="CLICK ME",
                 font="Roboto", font_size=16, font_color=(0, 0, 0, 1),
                 bold=False, italic=False, underline=False, strikethrough=False,
                 button_color=(0, 0.5, 0.5, 1), hover_opacity=0.7, clicked_opacity=0.5,
                 border_color=(1, 1, 0, 1), border_thickness=0, corner_radius=0,
                 shadow_color=(1, 1, 1, 0), shadow_offset=(0, 0),
                 blur_radius=0, spread_radius=(0, 0),
                 is_visible=True, is_disabled=False, disabled_opacity=0.3, opacity=1,
                 on_hover=None, on_click=None, on_release=None, tag=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)  # Explicitly disable size_hint

        self.window = window
        self.size = (width, height)
        self.pos = (x, y)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
        self.button_color = button_color
        self.hover_opacity = hover_opacity
        self.clicked_opacity = clicked_opacity
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.corner_radius = self._check_four_or_one_value(corner_radius)
        self.on_click = on_click
        self.on_release = on_release
        self.on_hover = on_hover
        self.tag = tag
        self.is_pressed = False
        self.is_disabled = is_disabled
        self.disabled_opacity = disabled_opacity
        self.is_visible = is_visible
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset
        self.blur_radius = blur_radius
        self.spread_radius = spread_radius

        # Apply markup to the text
        self.text = self.apply_markup(self.text)

        # Register font if provided
        if font.endswith((".ttf", ".otf")):
            LabelBase.register(name="CustomFont", fn_regular=font)
            self.font = "CustomFont"

        # Add the button text as a label
        self.label = Label(
            text=self.text,
            font_name=self.font,
            font_size=self.font_size,
            color=self.font_color,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
            halign="center",
            valign="middle",
            markup=True
        )

        self._update_canvas()
        # Draw the border if thickness is greater than 0
        # with self.canvas.before:
            # # Draw shadow
            # Color(*self.shadow_color)
            # self.shadow = BoxShadow(
            #     pos=(self.pos[0] + self.shadow_offset[0], self.pos[1] + self.shadow_offset[1]),
            #     size=self.size,
            #     offset=self.shadow_offset,
            #     blur_radius=self.blur_radius,
            #     spread_radius=self.spread_radius,
            #     border_radius=self.corner_radius
            # )
            # Draw the rounded rectangle background
            # self.bg_color = Color(*self.button_color)
            # self.bg_color.a = opacity  # Apply initial opacity
            # self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.corner_radius)

            # self._draw_borders()



        if window:
            # Add to the provided pyvisual window
            self.add_widget(self.label)
            self.window.add_widget(self)
        else:
            self.add_widget(self.label)

        self.set_visibility(self.is_visible)
        self.set_opacity(opacity)

        # Bind mouse position for hover detection
        KivyWindow.bind(mouse_pos=self.on_mouse_pos)
        self.label.bind(size=self._update_text, pos=self._update_text)

        # Bind position and size updates
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        # self.bind(size=self._draw_borders, pos=self._draw_borders)


        # Bind the opacity property to update the canvas
        self.bind(opacity=self._on_opacity)

    def _check_four_or_one_value(self, value):
        """Normalize border_thickness to a tuple of four values (top, right, bottom, left)."""
        if isinstance(value, (int, float)):
            return (value, value, value, value)
        elif isinstance(value, (list, tuple)) and len(value) == 4:
            return tuple(value)
        else:
            raise ValueError("Value must be a single value or a tuple/list of four values")

    def _draw_borders(self,*args):
        """Draw borders with different thicknesses for each side."""
        with self.canvas.before:
            self.border_color_instruction = Color(*self.border_color)  # RGBA border color
            if isinstance(self.border_thickness, (int, float)):
                if self.border_thickness > 0:

                    self.border_line = Line(
                        rounded_rectangle=(
                            self.pos[0] + self.border_thickness / 2,  # Shift inward
                            self.pos[1] + self.border_thickness / 2,  # Shift inward
                            self.size[0] - self.border_thickness,  # Reduce width
                            self.size[1] - self.border_thickness,  # Reduce height
                            *self._adjust_corner_radius(self.corner_radius, self.border_thickness)
                        ),
                        width=self.border_thickness
                    )

            else:
                top, right, bottom, left = self.border_thickness

                # Top border
                if top > 0:
                    Line(points=[
                        self.pos[0], self.pos[1] + self.size[1],  # Start point
                                     self.pos[0] + self.size[0], self.pos[1] + self.size[1]  # End point
                    ], width=top)

                # Right border
                if right > 0:
                    Line(points=[
                        self.pos[0] + self.size[0], self.pos[1] + self.size[1],  # Start point
                        self.pos[0] + self.size[0], self.pos[1]  # End point
                    ], width=right)

                # Bottom border
                if bottom > 0:
                    Line(points=[
                        self.pos[0] + self.size[0], self.pos[1],  # Start point
                        self.pos[0], self.pos[1]  # End point
                    ], width=bottom)

                # Left border
                if left > 0:
                    Line(points=[
                        self.pos[0], self.pos[1],  # Start point
                        self.pos[0], self.pos[1] + self.size[1]  # End point
                    ], width=left)

    def _adjust_corner_radius(self, corner_radius, border_thickness):
        """Adjust corner radius to account for border thickness."""
        return [max(0, r - border_thickness / 2) for r in corner_radius]

    def _update_canvas(self, *args):
        """Update the canvas elements when the button's size or position changes."""
        self.canvas.before.clear()
        #
        # # Update shadow properties
        # self.shadow.pos = (
        #     self.pos[0] + self.shadow_offset[0],
        #     self.pos[1] + self.shadow_offset[1]
        # )
        # self.shadow.size = self.size
        #
        # # Update button background
        # self.bg_rect.pos = self.pos
        # self.bg_rect.size = self.size
        # self.bg_rect.radius = self.corner_radius
        #
        # # Update border if thickness > 0
        with self.canvas.before:
            # Draw the rounded rectangle background
            self.bg_color = Color(*self.button_color)
            self.bg_color.a = self.opacity  # Apply initial opacity
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.corner_radius)


        self._draw_borders()

        # Center the label within the button
        self.label.pos = (
            self.pos[0] + (self.size[0] - self.label.size[0]) / 2,
            self.pos[1] + (self.size[1] - self.label.size[1]) / 2,
        )
        self.label.size = self.size


    def apply_markup(self, text):
        """Apply markup styles (bold, italic, underline, strikethrough) to text."""
        if self.strikethrough:
            text = f"[s]{text}[/s]"
        if self.underline:
            text = f"[u]{text}[/u]"
        if self.italic:
            text = f"[i]{text}[/i]"
        if self.bold:
            text = f"[b]{text}[/b]"
        return text
    def _update_text(self, *args):
        """Ensure the text is properly aligned within the button."""
        self.label.text_size = self.size  # Match label size to button size
        self.label.pos = self.pos  # Align label position with button


    def _on_opacity(self, instance, value):
        """Update the canvas opacity when the widget's opacity changes."""
        self.bg_color.a = value

    def on_mouse_pos(self, window, pos):
        """Handle mouse hover events."""
        if not self.is_disabled:
            if self.collide_point(*pos):
                if not self.is_pressed:
                    self.bg_color.a = self.hover_opacity  # Set hover opacity
                    if self.on_hover:
                        self.on_hover(self)
            else:
                self.bg_color.a = self.opacity  # Reset to idle state if not hovering

    def on_touch_down(self, touch):
        """Handle mouse click events."""
        if self.collide_point(*touch.pos):
            if not self.is_disabled:
                self.is_pressed = True
                self.bg_color.a = self.clicked_opacity  # Set click opacity
                if self.on_click:
                    self.on_click(self)
                return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """Handle mouse release events."""
        if self.is_pressed:
            self.is_pressed = False
            if not self.is_disabled:
                self.bg_color.a = self.hover_opacity if self.collide_point(*touch.pos) else self.opacity
                if self.on_release:
                    self.on_release(self)
            return True
        return super().on_touch_up(touch)

    def set_visibility(self, is_visible):
        """Set button visibility."""
        self.is_visible = is_visible
        self.opacity = 1 if self.is_visible else 0

    def set_disabled(self, is_disabled):
        """Enable or disable the button."""
        self.is_disabled = is_disabled
        self.opacity = self.disabled_opacity if self.is_disabled else 1
        self._update_disabled_state()

    def set_opacity(self, opacity):
        """Set button opacity."""
        self.opacity = opacity

    def set_text(self, text):
        """
        Set the text of the button and update the label.
        :param text: New text for the button.
        """
        self.text = self.apply_markup(text)  # Apply markup styles
        self.label.text = self.text  # Update the label's text
        self._update_text()

    def set_color(self, color):
        """
        Set the button's color and update the canvas.
        :param color: New RGBA color for the button.
        """

        self.button_color = color
        self.canvas.before.clear()  # Clear previous canvas instructions
        with self.canvas.before:
            # Draw the rounded rectangle background
            self.bg_color = Color(*self.button_color)
            self.bg_color.a = self.opacity  # Apply initial opacity
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.corner_radius)

    def set_font_color(self,color):
        self.label.color = color

    def set_border(self,border_thickness,color=None):
        if color:
            self.border_color = color
        self.border_thickness = border_thickness
        self._draw_borders()


    def _update_disabled_state(self):
        """Update the button appearance based on the disabled state."""
        if self.is_disabled:
            self.bg_color.a = self.disabled_opacity
        else:
            self.bg_color.a = self.opacity

    def add_to_layout(self, layout):
        """Add the image to a layout."""
        if self.parent is not None:
            self.parent.remove_widget(self)

        layout.add_widget(self)

if __name__ == "__main__":
    import pyvisual as pv

    # Create a pyvisual window
    window = pv.Window()

    button10 = BasicButton(window,500,300)

    # # Create buttons with rounded edges
    button1 = BasicButton(
        window=window, x=325, y=275, width=200, height=60, text="Button 1",
        font_size=24, corner_radius=20, opacity=1, border_thickness=5, border_color=(1, 0, 0, 1),
        on_click=lambda btn: print(f"{btn.text} clicked"),
        on_release=lambda btn: print(f"{btn.text} released")
    )
    button2 = BasicButton(
        window=window, x=325, y=375, width=200, height=60, text="Button 2",
        font_size=24, corner_radius=0, opacity=1, border_thickness=0, border_color=(0, 1, 0, 1),
        on_click=lambda btn: print(f"{btn.text} clicked"),
        on_release=lambda btn: print(f"{btn.text} released"), button_color=(1,0,0,1)
    )

    button2.set_color((1,0,1,1))

    button = BasicButton(
        window=window,
        x=100, y=100,
        width=200, height=50,
        text="Custom Corners",
        corner_radius=0,  # Different radii for each corner
        button_color=(0.9, 0.9, 0.9, 1)
    )

    button.set_border(  (2,0,2,0),(1, 0, 0, 1),)
    # Show the window
    window.show()


