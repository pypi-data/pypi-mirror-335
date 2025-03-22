from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window


class CustomTab:
    def __init__(
        self,
        window,
        x, y,
        width=400,
        height=300,
        tabs=None,
        font_size=16,
        button_height=40,
        tab_button_idle_color=(0.9, 0.9, 0.9, 1),
        tab_button_active_color=(0.6, 0.6, 0.6, 1),
        tab_button_hover_color=(0.8, 0.8, 0.8, 1),
        container_background_color=(1, 1, 1, 1)
    ):
        """
        Custom Tab implementation with buttons for tabs and a floating layout for content.

        :param window: Parent window.
        :param x, y: Position of the tab container.
        :param width, height: Dimensions of the tab container.
        :param tabs: List of tuples [("Tab Name", Content Layout), ...].
        :param button_height: Height of the tab buttons.
        :param tab_button_idle_color: Background color for idle buttons.
        :param tab_button_active_color: Background color for active buttons.
        :param tab_button_hover_color: Background color for hovered buttons.
        :param container_background_color: Background color for the content area.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tabs = tabs if tabs is not None else []
        self.font_size = font_size
        self.button_height = button_height
        self.tab_button_idle_color = tab_button_idle_color
        self.tab_button_active_color = tab_button_active_color
        self.tab_button_hover_color = tab_button_hover_color
        self.container_background_color = container_background_color
        self.active_button = None

        # Create main layout
        self.layout = FloatLayout(size=(self.width, self.height), pos=(self.x, self.y))

        # Draw container background
        with self.layout.canvas.before:
            Color(*self.container_background_color)
            self.bg_rect = Rectangle(size=(self.width, self.height - self.button_height), pos=(self.x, self.y))

        self.layout.bind(size=self._update_background, pos=self._update_background)

        # Add buttons and content
        self.tab_buttons = []
        self.content_area = FloatLayout(size=(self.width, self.height - self.button_height),
                                        pos=(self.x, self.y))
        self.layout.add_widget(self.content_area)

        self._create_tabs(window)

        Window.bind(mouse_pos=self._on_mouse_move)

        window.add_widget(self.layout)

    def _create_tabs(self, window):
        """Create tab buttons using PyVisual classes and initialize the content."""

        button_width = self.width / len(self.tabs) if self.tabs else 100

        for idx, (tab_name, tab_content) in enumerate(self.tabs):
            button = pv.BasicButton(
                window=None,  # No auto-add
                x=self.x + idx * button_width,
                y=self.y + self.height - self.button_height,
                width=button_width,
                height=self.button_height,
                text=tab_name,
                font_size=self.font_size,
                idle_color=self.tab_button_idle_color,

                on_click=self._on_tab_selected
            )

            button.add_to_layout(self.layout)
            self.tab_buttons.append((button, tab_content))

        if self.tab_buttons:
            self._select_tab(self.tab_buttons[0][0])

    def _on_mouse_move(self, window, pos):
        """Handle hover effects manually."""
        for button, _ in self.tab_buttons:
            button.update_hover_color(pos)

    def _on_tab_selected(self, button):
        """Handle tab selection."""
        self._select_tab(button)

    def _select_tab(self, selected_button):
        """Highlight the selected tab and display its content."""
        self.active_button = selected_button
        for button, content in self.tab_buttons:
            if button == selected_button:
                button.update_button_color(self.tab_button_active_color)  # Pass active color
                self._display_content(content)  # Display content for the active tab
            else:
                button.update_button_color(self.tab_button_idle_color)  # Pass idle color

    def _display_content(self, content):
        """Display the selected tab's content in the content area."""
        self.content_area.clear_widgets()
        if hasattr(content, 'add_to_layout'):
            content.add_to_layout(self.content_area)
        else:
            self.content_area.add_widget(content)

    def _update_background(self, *args):
        """Update background size and position."""
        self.bg_rect.size = (self.width, self.height - self.button_height)
        self.bg_rect.pos = (self.x, self.y)

if __name__ == "__main__":
    import pyvisual as pv

    window = pv.Window()

    # Create PyVisual components for the content area

    tabs = [
        ("Tab 1", pv.BasicButton(window=None, x=50, y=50, width=200, height=60, text="Button in Tab 1")),
        ("Tab 2", pv.BasicButton(window=None, x=50, y=50, width=200, height=60, text="Button in Tab 2")),
        ("Tab 3", pv.BasicButton(window=None, x=50, y=50, width=200, height=60, text="Button in Tab 3"))
    ]

    custom_tab = CustomTab(
        window=window,
        x=100, y=0,
        width=400, height=300,
        tabs=tabs,
        font_size=18,
        tab_button_idle_color=(0.7, 0.7, 0.7, 1),
        tab_button_active_color=(0.3, 0.3, 0.3, 1),
        tab_button_hover_color=(0.5, 0.5, 0.5, 1),
        container_background_color=(0.9, 0.9, 0.9, 1)
    )

    window.show()
