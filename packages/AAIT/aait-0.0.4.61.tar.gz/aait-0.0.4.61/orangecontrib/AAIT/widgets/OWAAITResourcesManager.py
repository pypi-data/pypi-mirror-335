import os
import sys

from AnyQt import QtWidgets
from AnyQt.QtCore import QTimer
from AnyQt.QtWidgets import QApplication  # QMainWindow, QFileDialog
from AnyQt.QtWidgets import (QComboBox, QDialog, QGroupBox, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QVBoxLayout)
from Orange.widgets import widget

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.fix_torch import fix_torch_dll_error
    from Orange.widgets.orangecontrib.AAIT.utils import (MetManagement,
                                                         SimpleDialogQt)
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import (
        GetFromRemote, get_aait_store_requirements_json)
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.fix_torch import fix_torch_dll_error
    from orangecontrib.AAIT.utils import (MetManagement,
                                                         SimpleDialogQt)
    from orangecontrib.AAIT.utils.MetManagement import (
        GetFromRemote, get_aait_store_requirements_json)
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
fix_torch_dll_error.fix_error_torch()

@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWAAITResourcesManager(widget.OWWidget):
    name = "AAIT Resources Manager"
    description = "Manage AAIT resources, such as model, example workflows, datasets...."
    icon = "icons/documents.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/documents.png"
    priority = 1001
    # Path
    dossier_du_script = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        super().__init__()
        self.requirements = get_aait_store_requirements_json()
        self.controlAreaVisible = False

    # trigger if standard windows is opened
    def showEvent(self, event):
        super().showEvent(event)
        self.show_dialog()
        # We cannot close the standard ui widget it is displayed
        # so it makes a little tinkles :(
        QTimer.singleShot(0, self.close)

    def show_dialog(self):

        # third-party code execution vs standard code execution
        if False == os.path.isfile(MetManagement.get_local_store_path() + "AddOn/prefix_show_dialog.py"):
            dialog = QDialog()
            layout_a = QVBoxLayout()
            dialog.setLayout(layout_a)
            model = None
        else:
            sys.path.append(MetManagement.get_local_store_path() + "AddOn")
            import prefix_show_dialog
            stable_dependency = True
            if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
                stable_dependency = False
            dialog, model = prefix_show_dialog.prefix_dialog_function(self,stable_dependency)

        # download section
        # Creation of vertical layout
        main_layout = QVBoxLayout()
        group_box = QGroupBox("Download new minimum working example")
        group_layout = QVBoxLayout()

        # Elements are presented horizontally
        h_layout = QHBoxLayout()
        v_layout_button_combo_box = QVBoxLayout()
        self.comboBox = QComboBox()
        self.comboBox.setMinimumSize(200, 10)
        self.ressource_path_button = QPushButton('Select repository')
        self.saveButton = QPushButton('Download')
        self.reloadButton = QPushButton('Reload')  # Bouton ajouté
        self.label_info = QLabel('')

        v_layout_button_combo_box.addWidget(self.ressource_path_button)
        verticalSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        v_layout_button_combo_box.addItem(verticalSpacer)
        v_layout_button_combo_box.addWidget(self.comboBox)
        v_layout_button_combo_box.addWidget(self.saveButton)
        v_layout_button_combo_box.addWidget(self.reloadButton)  # Bouton ajouté à l'interface
        v_layout_button_combo_box.addWidget(self.label_info)
        h_layout.addLayout(v_layout_button_combo_box)
        h_layout.setSpacing(5)
        v_layout_button_combo_box.setSpacing(5)
        v_layout_label_text = QVBoxLayout()
        v_layout_label_text.setSpacing(5)
        label = QLabel('Description:')
        self.descriptionTextEdit = QTextEdit()
        self.descriptionTextEdit.setMaximumHeight(80)
        v_layout_label_text.addWidget(label)
        v_layout_label_text.addWidget(self.descriptionTextEdit)
        h_layout.addLayout(v_layout_label_text)

        group_layout.addLayout(h_layout)
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)
        main_layout.setContentsMargins(5, 5, 5, 5)
        dialog.layout().insertLayout(0, main_layout)

        self.comboBox.currentIndexChanged.connect(self.handleComboBoxChange)
        self.saveButton.clicked.connect(self.saveFile)
        self.reloadButton.clicked.connect(self.reload_resources)  # Connexion du bouton Recharger
        self.ressource_path_button.clicked.connect(self.update_ressource_path)
        self.populate_combo_box()

        if False == os.path.isfile(MetManagement.get_local_store_path() + "AddOn/postfix_show_dialog.py"):
            dialog.exec()
        else:
            sys.path.append(MetManagement.get_local_store_path() + "AddOn")
            import postfix_show_dialog
            stable_dependency = True
            if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
                stable_dependency = False
            postfix_show_dialog.postfix_dialog_function(dialog, model)

    def populate_combo_box(self):
        # clean combo box if we change of repository
        self.comboBox.clear()
        workflows = []
        descriptions = dict()
        if self.requirements==None:
            return
        for element in self.requirements:
            workflows.append(element["name"])
            descriptions[element["name"]] = element["description"][0]
        self.descriptions = descriptions
        self.comboBox.addItems(workflows)

    def handleComboBoxChange(self, index):
        selected_file = self.comboBox.itemText(index)
        if selected_file=="":
            return
        # print description in QTextEdit
        self.descriptionTextEdit.setPlainText(self.descriptions[selected_file])

    def read_description(self, file_name):
        # Chemin du fichier texte contenant la description
        description_file_path = os.path.join(self.dossier_du_script, 'ows_example',
                                             f'{os.path.splitext(file_name)[0]}.txt')
        # Lire le contenu du fichier s'il existe, sinon retourner une chaîne vide
        if os.path.exists(description_file_path):
            with open(description_file_path, 'r') as file:
                description = file.read()
        else:
            description = ""
        return description

    def saveFile(self):
        # Méthode pour sauvegarder le fichier sélectionné dans un nouvel emplacement
        self.label_info.setText('Synchronization in progress')
        QApplication.processEvents()  # Pour actualiser l'interface utilisateur



        selected_file = self.comboBox.currentText()
        GetFromRemote(selected_file)
        self.label_info.setText('')

    def update_ressource_path(self):
        folder = MetManagement.get_aait_store_remote_ressources_path()
        file=SimpleDialogQt.BoxSelectExistingFile(self, default_dir=folder, extention="Aiit file (*.aait)")
        if file == "":
            return
        if MetManagement.get_size(file)==0:
            folder=os.path.dirname(os.path.abspath(file)).replace("\\", "/")
            if folder == "":
                return
            if folder[-1]!="/":
                folder+="/"
            MetManagement.set_aait_store_remote_ressources_path(folder)
        else:
            #compressed case
            file=file.replace("\\", "/")
            MetManagement.set_aait_store_remote_ressources_path(file)
        self.requirements = get_aait_store_requirements_json()
        self.populate_combo_box()

    def reload_resources(self):
        """Fonction appelée lorsque le bouton Recharger est cliqué."""
        self.requirements = get_aait_store_requirements_json()
        self.populate_combo_box()
        self.label_info.setText('Resources reloaded successfully.')

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = OWAAITResourcesManager()
    window.show()
    app.exec_()
