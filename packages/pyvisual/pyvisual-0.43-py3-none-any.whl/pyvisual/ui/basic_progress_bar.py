from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label

class BasicProgressBar(Widget):
    progress = NumericProperty()
    max_progress = NumericProperty()
    bar_color = ListProperty()
    background_color = ListProperty()
    show_text = StringProperty()
    font_name = StringProperty()
    font_size = NumericProperty()
    font_color = ListProperty()
    padding = NumericProperty()

    def __init__(self, window, x, y, width=200, height=30,
                 progress=0, max_progress=100,
                 bar_color=[0.2, 0.6, 0.9, 0.8], background_color=[0.9, 0.9, 0.9, 1],
                 show_text='center', font_name='Roboto', font_size=14, font_color=[0.5, 0.5, 0.5, 1],
                 padding=0,
                 **kwargs):
        super().__init__(**kwargs)
        self.window = window
        self.pos = (x, y)
        self.size = (width, height)
        self.size_hint = (None, None)

        # Initialize properties with input parameters
        self.progress = progress
        self.max_progress = max_progress
        self.bar_color = bar_color
        self.background_color = background_color
        self.show_text = show_text
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.padding = padding  # Padding can be negative or positive

        # Draw the progress bar
        with self.canvas:
            # Background
            self.bg_color_instruction = Color(rgba=self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            # Progress bar
            self.bar_color_instruction = Color(rgba=self.bar_color)
            self.bar_rect = Rectangle(pos=self.pos, size=(0, self.height))

        # Create the Label to display the progress text
        self.progress_label = Label(
            text=f"{int(self.progress / self.max_progress * 100)}%",
            font_name=self.font_name,
            font_size=self.font_size,
            color=self.font_color,
            size_hint=(None, None),
            halign='left',  # Will adjust based on alignment
            valign='middle',
        )

        # Add the label to the widget
        self.add_widget(self.progress_label)

        # Bind properties to update methods
        self.bind(pos=self.update_all,
                  size=self.update_all,
                  progress=self.update_progress,
                  bar_color=self.update_bar_color,
                  background_color=self.update_background_color,
                  show_text=self.update_text_alignment,
                  font_name=self.update_font_properties,
                  font_size=self.update_font_properties,
                  font_color=self.update_font_properties,
                  padding=self.update_padding)  # Bind padding property

        # Initial updates
        self.update_all()

        # Add the widget to the window
        window.add_widget(self)

    def update_all(self, *args):
        self.update_rectangles()
        self.update_label_properties()

    def update_rectangles(self, *args):
        # Update the positions and sizes of the rectangles
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        progress_width = (self.progress / self.max_progress) * self.width
        self.bar_rect.pos = self.pos
        self.bar_rect.size = (progress_width, self.height)

    def update_label_properties(self, *args):
        alignment = self.show_text.lower()
        padding = self.padding

        # Base label position and size
        label_x, label_y = self.pos
        label_width, label_height = self.size

        if alignment == 'left':
            self.progress_label.halign = 'left'

            if padding >= 0:
                # Positive padding moves text right
                self.progress_label.pos = (label_x + padding, label_y)
                self.progress_label.size = (label_width - padding, label_height)
            else:
                # Negative padding moves text left; extend label width
                self.progress_label.pos = (label_x + padding, label_y)
                self.progress_label.size = (label_width - padding, label_height)
        elif alignment == 'center':
            self.progress_label.halign = 'center'
            self.progress_label.pos = (label_x, label_y)
            self.progress_label.size = (label_width, label_height)
            padding = 0  # Ignore padding for center alignment
        elif alignment == 'right':
            self.progress_label.halign = 'right'

            if padding >= 0:
                # Positive padding moves text left
                self.progress_label.pos = (label_x, label_y)
                self.progress_label.size = (label_width - padding, label_height)
            else:
                # Negative padding moves text right; extend label width
                self.progress_label.pos = (label_x, label_y)
                self.progress_label.size = (label_width - padding, label_height)
        else:
            self.progress_label.text = ''  # Hide text if 'none' or invalid value

        # Set text size to label size
        self.progress_label.text_size = self.progress_label.size
        # Set padding
        self.progress_label.padding = (0, 0, 0, 0)

        self.progress_label.texture_update()

    def update_progress(self, *args):
        # Update the size of the progress bar rectangle
        progress_width = (self.progress / self.max_progress) * self.width
        self.bar_rect.size = (progress_width, self.height)

        # Update the label text
        if self.max_progress == 0:
            percentage = 0
        else:
            percentage = int(self.progress / self.max_progress * 100)
        if self.show_text.lower() != 'none':
            self.progress_label.text = f"{percentage}%"
        else:
            self.progress_label.text = ''

        # Update label properties
        self.update_label_properties()

    def update_bar_color(self, *args):
        # Update the color of the progress bar
        self.bar_color_instruction.rgba = self.bar_color

    def update_background_color(self, *args):
        # Update the background color
        self.bg_color_instruction.rgba = self.background_color

    def update_text_alignment(self, *args):
        # Update label properties when alignment changes
        self.update_label_properties()

    def update_font_properties(self, *args):
        # Update font properties
        self.progress_label.font_name = self.font_name
        self.progress_label.font_size = self.font_size
        self.progress_label.color = self.font_color
        self.progress_label.texture_update()

        # Update label properties
        self.update_label_properties()

    def update_padding(self, *args):
        # Update label properties when padding changes
        self.update_label_properties()

    def set_progress(self, value):
        """Set the progress value."""
        self.progress = max(0, min(value, self.max_progress))

    def get_progress(self):
        """Get the current progress value."""
        return self.progress


if __name__ == "__main__":
    from kivy.clock import Clock
    import pyvisual as pv

    window = pv.Window()

    # Create an instance of BasicProgressBar with left alignment and negative padding
    progress_bar = BasicProgressBar(
        window=window,
        x=100,
        y=300,
        width=400,
        height=30,
        progress=50,
        max_progress=100,
        bar_color=[0.2, 0.6, 0.9, 0.8],
        background_color=[0.9, 0.9, 0.9, 1],
        show_text='right',          # Display text on the left
        font_name='Roboto',
        font_size=18,
        font_color=[0.1, 0.1, 0.1, 1],
    )

    # Function to simulate progress
    def increment_progress(dt):
        new_progress = progress_bar.get_progress() + 5
        if new_progress > progress_bar.max_progress:
            new_progress = 0  # Reset progress
        progress_bar.set_progress(new_progress)

    # Schedule the progress increment
    Clock.schedule_interval(increment_progress, 0.5)  # Update every 0.5 seconds

    window.show()
