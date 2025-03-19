from pyvisual.ui.inputs.pv_button import PvButton
from PySide6.QtWidgets import QFileDialog


class PvFileUploader(PvButton):
    """
    A file uploader button that opens a file dialog on click,
    with a dashed border style, and optionally supports file drag-and-drop.

    :param container: The parent container.
    :param file_filter: The file filter for the file dialog.
    :param on_file_selected: A callback function called when a file is selected.
    :param enable_drag_drop: If True, allows drag-and-drop of files onto the button.
    """

    def __init__(self, container, file_filter="All Files (*.*)", on_file_selected=None, enable_drag_drop=False,
                 **kwargs):
        super().__init__(container, **kwargs)
        # Use the setters to initialize the new properties.
        self.file_filter = file_filter
        self.on_file_selected = on_file_selected
        self.enable_drag_drop = enable_drag_drop

        self._on_click = self.upload_file
        # self.configure_style()

    def upload_file(self, btn):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.file_filter)
        if file_path:
            file_name = file_path.split("/")[-1]
            self.text = file_name
            if self.on_file_selected:
                self.on_file_selected(file_path)

    # --- Drag & Drop Event Handlers ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            # Only process the first file dropped
            file_path = urls[0].toLocalFile()
            file_name = file_path.split("/")[-1]
            self.text = file_name
            if self.on_file_selected:
                self.on_file_selected(file_path)

    # --- New Getter and Setter Properties ---
    @property
    def file_filter(self):
        return self._file_filter

    @file_filter.setter
    def file_filter(self, value):
        self._file_filter = value

    @property
    def on_file_selected(self):
        return self._on_file_selected

    @on_file_selected.setter
    def on_file_selected(self, callback):
        self._on_file_selected = callback

    @property
    def enable_drag_drop(self):
        return self._enable_drag_drop

    @enable_drag_drop.setter
    def enable_drag_drop(self, flag):
        self._enable_drag_drop = flag
        self.setAcceptDrops(flag)


# ------------------------------------------------------------------------------
# Example Usage
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import pyvisual as pv

    app = pv.PvApp()
    window = pv.PvWindow(title="PvFileUploader Example", is_resizable=True)


    # Callback function to handle the file selection.
    def file_selected_callback(file_path):
        print(f"Selected file: {file_path}")


    # Create a PvFileUploader with drag-and-drop enabled.
    file_uploader = PvFileUploader(window, x=50, y=150, width=300, height=300,
                                   text="Upload File", font_size=14,
                                   font_color=(50, 50, 50, 0.75),
                                   corner_radius=10,
                                   border_thickness=2,
                                   border_style="dotted",
                                   button_color=(50, 50, 50, 0.1),
                                   hover_color=(50, 50, 50, 0.15),
                                   clicked_color=(50, 50, 50, 0.1),
                                   file_filter="Images (*.png *.jpg *.jpeg);;All Files (*.*)",
                                   on_file_selected=file_selected_callback,
                                   enable_drag_drop=True)

    window.show()
    app.run()
