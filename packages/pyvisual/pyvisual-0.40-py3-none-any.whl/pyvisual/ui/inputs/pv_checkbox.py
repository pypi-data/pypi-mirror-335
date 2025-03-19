from PySide6.QtWidgets import QLabel, QCheckBox, QApplication, QWidget
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtCore import Qt


class PvCheckbox(QCheckBox):
    def __init__(self, container, x=0, y=0, size=30, padding=4, visibility=True,
                 checked_color=(76, 204, 76, 255), unchecked_color=(255, 255, 255, 255),
                 border_color=(76, 76, 76, 255), border_thickness=0, is_checked=False,
                 toggle_callback=None, text="Option 1", text_position='right', corner_radius=8,
                 text_padding=5, font_name='Roboto', font_color=(0, 0, 0, 255),
                 font_size=14, font_hover_color=None, **kwargs):
        super().__init__(container)

        # Attributes
        self._x = x
        self._y = y
        self._size = size
        self._padding = padding
        self._checked_color = checked_color
        self._unchecked_color = unchecked_color
        self._border_color = border_color
        self._border_thickness = border_thickness
        self._toggle_callback = toggle_callback
        self._text = text
        self._text_position = text_position
        self._corner_radius = corner_radius
        self._text_padding = text_padding
        self._font_name = font_name
        self._font_color = font_color
        self._font_size = font_size
        self._font_hover_color = font_hover_color or font_color

        # Hide the default checkbox indicator
        self.setStyleSheet("QCheckBox::indicator { width: 0; height: 0; }")

        # Set position and size
        self.setGeometry(self._x, self._y, self._size + self._padding * 2, self._size + self._padding * 2)
        self.setChecked(is_checked)

        # Text label if provided
        if self._text:
            self._text_label = QLabel(self._text, container)
            self._apply_text_style(self._font_color)
            self._set_text_position()

        # Connect signals
        self.stateChanged.connect(self._on_toggle)

    def mousePressEvent(self, event):
        """Override mousePressEvent to toggle state manually."""
        super().mousePressEvent(event)
        self.setChecked(not self.isChecked())  # Toggle state
        self.update()  # Trigger repaint

    def enterEvent(self, event):
        """Handles hover (mouse enter) events."""
        super().enterEvent(event)
        if self._text and hasattr(self, "_text_label"):
            self._apply_text_style(self._font_hover_color)

    def leaveEvent(self, event):
        """Handles hover (mouse leave) events."""
        super().leaveEvent(event)
        if self._text and hasattr(self, "_text_label"):
            self._apply_text_style(self._font_color)

    def _on_toggle(self, state):
        self.update()  # Trigger a repaint
        if self._toggle_callback:
            self._toggle_callback(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw outer border
        painter.setPen(QColor(*self._border_color))
        painter.setBrush(QColor(*self._unchecked_color))
        painter.drawRoundedRect(self._padding, self._padding,
                                self._size, self._size,
                                self._corner_radius, self._corner_radius)

        # Draw inner shape if checked
        if self.isChecked():
            inner_size = self._size - 2 * self._padding
            inner_x = self._padding
            inner_y = self._padding
            painter.setBrush(QColor(*self._checked_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(inner_x+self._padding, inner_y+self._padding, inner_size, inner_size,
                                    self._corner_radius, self._corner_radius)
        painter.end()

    def _apply_text_style(self, color):
        """Apply font style to the text label."""
        if hasattr(self, "_text_label"):
            self._text_label.setFont(QFont(self._font_name, self._font_size))
            self._text_label.setStyleSheet(
                f"color: rgba({color[0]}, {color[1]}, {color[2]}, {color[3]});"
            )

    def _set_text_position(self):
        """Position the text label based on the specified position."""
        self._text_label.adjustSize()
        text_width = self._text_label.width()
        text_height = self._text_label.height()
        checkbox_x = self._x
        checkbox_y = self._y
        checkbox_size = self._size + self._padding * 2

        if self._text_position == 'left':
            self._text_label.setGeometry(
                checkbox_x - text_width - self._text_padding,
                checkbox_y + (checkbox_size - text_height) // 2,
                text_width,
                text_height
            )
        elif self._text_position == 'right':
            self._text_label.setGeometry(
                checkbox_x + checkbox_size + self._text_padding,
                checkbox_y + (checkbox_size - text_height) // 2,
                text_width,
                text_height
            )
        elif self._text_position == 'top':
            self._text_label.setGeometry(
                checkbox_x + (checkbox_size - text_width) // 2,
                checkbox_y - text_height - self._text_padding,
                text_width,
                text_height
            )
        elif self._text_position == 'bottom':
            self._text_label.setGeometry(
                checkbox_x + (checkbox_size - text_width) // 2,
                checkbox_y + checkbox_size + self._text_padding,
                text_width,
                text_height
            )

if __name__ == "__main__":
    import pyvisual as pv
    app = pv.PvApp()

    # Create a window
    window = pv.PvWindow(title="PvApp Example")

    # Add a text widget
    checkbox = PvCheckbox(
        container=window,
        x=50, y=50,
        size=100,
        font_size=25,
        padding=10,
        corner_radius=50,
        text="Check me!",
        text_position='right',
        checked_color=(0, 128, 0, 255),
        unchecked_color=(255, 255, 255, 255),
        border_color=(0, 0, 0, 255),
        toggle_callback=lambda cb: print(f"Checked: {cb.isChecked()}")
    )



    myGroup = pv.PvGroupLayout(window)
    checkbox = pv.PvCheckbox(container=myGroup)

    # Show the window
    window.show()

    # Run the application
    app.run()

