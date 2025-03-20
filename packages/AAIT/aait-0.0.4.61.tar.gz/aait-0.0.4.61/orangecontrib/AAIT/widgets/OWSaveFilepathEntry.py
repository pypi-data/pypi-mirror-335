import json
import os
import tempfile
from pathlib import Path
from typing import Union

import Orange
from AnyQt.QtWidgets import QLineEdit, QMessageBox
from Orange.data.io import CSVReader
from Orange.data.table import Table
from Orange.widgets import gui, widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import Input
# add jcmhkh
import pickle
import Orange


class OWSaveFilepathEntry(widget.OWWidget):
    name = "Save with Filepath Entry"
    description = "Save data to a local interface. The file path is entered manually."
    icon = "icons/owsavefilepathentry.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owsavefilepathentry.svg"
    priority = 1220
    want_main_area = False
    resizing_enabled = False

    class Inputs:
        data = Input("Data", Table)
        path = Input("Path", str)

    # Persistent settings for fileId and CSV delimiter
    filename: str = Setting("embeddings.pkl") # type: ignore

    def __init__(self):
        super().__init__()
        self.info_label = gui.label(self.controlArea, self, "Initial info.")
        self.data = None
        self.save_path: str | None =None
        self.setup_ui()


    def setup_ui(self):
        """Set up the user interface."""
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)


    @Inputs.data
    def dataset(self, data): 
        """Handle new data input."""
        self.data = data
        if self.data is not None:
            self.save_to_file()

    
    @Inputs.path
    def path(self, path):
        """Handle new path input."""
        if isinstance(path, str):
            path_str = path
        else:
            print("path type: ", type(path))
            print("path: ", path)
            QMessageBox.warning(self, "Invalid Path", "Invalid path input. Only string paths are supported.")
            return
        
        self.save_path = path_str
        if self.save_path is not None:
            self.save_to_file()

    def save_to_file(self):
        """Save data to a file."""
        if self.data is None:
            return

        if self.save_path is None:
            self.info_label.setText("No file path specified.")
            return

        if os.path.isdir(self.save_path):
            self.save_path = os.path.join(self.save_path, self.filename)
        if len(self.save_path)>4:
            if self.save_path[-3:]!="pkl":
                import Orange.widgets.data.owsave as save_py

                saver = save_py.OWSave()
                saver.data = self.data
                saver.filename = self.save_path
                saver.add_type_annotations=True
                saver.do_save()
                return

        # add jcmhkh
        with open(self.save_path, "wb") as f:
            print("warning hard save pikle!")
            pickle.dump(self.data, f)



if __name__ == "__main__": 
    WidgetPreview(OWSaveFilepathEntry).run()
