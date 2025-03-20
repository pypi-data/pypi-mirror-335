from kivy.uix.image import Image as KivyImage


class Image(KivyImage):
    def __init__(self, window=None, x=0, y=0, image_path="", scale=1.0, is_visible=True, opacity=1, tag=None):
        super().__init__(source=image_path, size_hint=(None, None), pos=(x, y))

        self.scale_factor = scale
        self.tag = tag
        self.is_visible = is_visible  # Initialize is_visible state

        # Set scaling and positioning
        self.set_scale(self.scale_factor)


        # If auto_add is True and window is provided, add immediately
        if window:
            window.add_widget(self)
        self.opacity = opacity
        self.bind(opacity=self._on_opacity)
        self.opacity = opacity  # Trigger the opacity bindinge canvas to update
        self.set_visibility(self.is_visible)
    def set_scale(self, scale):
        """Scale the image based on the scale parameter."""
        self.width = self.texture_size[0] * scale
        self.height = self.texture_size[1] * scale

    def set_position(self, x, y):
        """Update the position of the image."""
        self.pos = (x, y)

    def set_image(self, image_path):
        """Set a new image."""
        self.source = image_path
        self.reload()  # Reload the texture for the new image

    def set_visibility(self, is_visible):
        """Show or hide the image."""
        if is_visible:
            self.opacity = 1
        else:
            self.opacity = 0

        self.is_visible = is_visible

    def add_to_layout(self, layout):
        """Add the image to a layout."""
        if self.parent is not None:
            self.parent.remove_widget(self)
        layout.add_widget(self)

    def _on_opacity(self, instance, value):
        """Update the canvas opacity when the widget's opacity changes."""
        self.opacity = value
        self.canvas.opacity = value

    def set_opacity(self, opacity):
        self.opacity = opacity
        self.canvas.opacity = opacity


if __name__ == "__main__":
    import pyvisual as pv

    window = pv.Window()

    # Create and add an image
    img1 = Image(window=window, x=50, y=50, image_path="../assets/buttons/blue_round/idle.png", scale=1.5, )
    img2 = Image(window=window, x=300, y=50, image_path="../assets/buttons/blue_round/idle.png", scale=1.0,
                 is_visible=False)
    window.show()
