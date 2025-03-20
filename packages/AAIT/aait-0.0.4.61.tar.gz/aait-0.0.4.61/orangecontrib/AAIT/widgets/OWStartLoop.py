import copy
import os
import sys

import Orange.data
from AnyQt.QtWidgets import QPushButton
from Orange.data import Domain, StringVariable
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.widget import Output, OWWidget

class LoopStartWidget(OWWidget):
    name = "Loop Start"
    description = "Widget to start a loop with data table input and output."
    icon = "icons/startloop.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/startloop.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owstartloop.ui")
    want_control_area = False
    priority = 1010

    class Inputs:
        data_in = Input("Data In", Orange.data.Table)
        # in_pointer = Input("End of the Loop Do-While", str, auto_summary=False)

    class Outputs:
        data_out = Output("Data Out", Orange.data.Table)
        out_pointer = Output("Begin of the Loop Do-While", str, auto_summary=False)

    def __init__(self):
        super().__init__()

        # Add button
        self.activate_button = QPushButton("Activer", self)
        self.activate_button.setCheckable(True)
        self.activate_button.setChecked(False)  # Le bouton est activé par défaut
        self.activate_button.clicked.connect(self.on_activate_button_clicked)
        self.mainArea.layout().addWidget(self.activate_button)

        self.data = None
        self.send_pointer()

    def on_activate_button_clicked(self):
        if self.activate_button.isChecked():
            self.information("Le bouton est activé !")
            self.activate_button.setText("Désactiver")
        else:
            self.information("Le bouton est désactivé !")
            self.activate_button.setText("Activer")

    @Inputs.data_in
    def set_data(self, dataset):
        if dataset is None:
            print("No data received.")
            return
        self.error("")
        # Verify data type
        print("Data received in set_data:")
        print(dataset)

        if isinstance(dataset, list):
            self.receive_table_representation(dataset)
        elif isinstance(dataset, Orange.data.Table):
            # Verifiy if we recive a data table (from the in_data)
            for el_domain in dataset.domain.variables + dataset.domain.metas:
                if not isinstance(el_domain, (Orange.data.StringVariable, Orange.data.ContinuousVariable)):
                    self.error(f"Error {type(el_domain)}: This widget can only be used with StringVariable or ContinuousVariable")
                    return

            self.data = copy.deepcopy(dataset)

            self.process_data()
        else:
            self.error("Unsupported data type received in set_data.")
            return

    def receive_table_representation(self, table_representation):
        """Receive the table representation from the end loop and update the values in self.data."""
        try:
            for col in table_representation:
                print(f"Name: {col['name']}, Type: {col['type']}, Values: {col['values']}")

            # Checking if self.data is defined as orange data table
            if self.data is None:
                self.error("No initial data to update.")
                print("self.data is None. Exiting the function.")
                return
            else:
                print("self.data is defined.")

            # Checking if colum form data init and table_representation are the same
            column_names = [col['name'] for col in table_representation]

            data_column_names = [var.name for var in self.data.domain.variables + self.data.domain.metas]

            if set(column_names) != set(data_column_names):
                self.error("column form data entry and now are diffrent.")
                return



            # Starting to update self.data with values from table_representation
            for col in table_representation:
                col_name = col['name']
                col_values = col['values']
                print(f"Processing column '{col_name}'...")

                # Check if the column is in attribut
                attribute_names = [var.name for var in self.data.domain.attributes]
                meta_names = [var.name for var in self.data.domain.metas]
                print("Attribute names:", attribute_names)
                print("Meta names:", meta_names)

                if col_name in attribute_names:
                    print(f"Column '{col_name}' is in attributes.")
                    col_index = self.data.domain.index(col_name)
                    print(f"Index of column '{col_name}' in attributes:", col_index)
                    for i in range(len(self.data)):
                        print(f"Updating self.data.X[{i}, {col_index}] with value: {col_values[i]}")
                        self.data.X[i, col_index] = col_values[i]

                # Check if the colum is in meta
                elif col_name in meta_names:
                    print(f"Column '{col_name}' is in metas.")
                    col_index = self.data.domain.metas.index(self.data.domain[col_name])
                    print(f"Index of column '{col_name}' in metas:", col_index)
                    for i in range(len(self.data)):
                        print(f"Updating self.data.metas[{i}, {col_index}] with value: {col_values[i]}")
                        self.data.metas[i, col_index] = col_values[i]
                else:
                    print(f"Column '{col_name}' not found in self.data.")
                    self.error(f"Column {col_name} not found in self.data.")
                    return



            # Calling self.process_data() to process updated data.
            self.process_data()

        except Exception as e:
            self.error("Failed to receive table representation: " + str(e))
            print("Error in receive_table_representation:", e)

    def get_nb_line(self):
        """Return the number of lines to be called from another widget."""
        return 0 if self.data is None else len(self.data)

    def get_column_name_and_type(self):
        """Return the name and type of 'data_in' to be called from another widget."""
        if self.data is None:
            return [[], []]
        column_names = []
        column_types = []

        for element in self.data.domain.variables + self.data.domain.metas:
            column_names.append(str(element.name))
            column_types.append(str(type(element)))
        return column_names, column_types

    def process_data(self):
        """Main process executed when data is available."""
        if self.data is not None and self.activate_button.isChecked():

            if 'data_out' not in [meta.name for meta in self.data.domain.metas]:
                self.add_data_out_column()

            self.Outputs.data_out.send(self.data)  # Envoie les données en sortie
        else:
            print("No data sent. The activate button is not checked or no data received.")

    def add_data_out_column(self):
        """Add the 'data_out' column if it doesn't already exist."""
        data_out_column = StringVariable("data_out")
        new_domain = Domain(self.data.domain.attributes, self.data.domain.class_vars,
                            metas=self.data.domain.metas + (data_out_column,))
        new_data = Orange.data.Table.from_table(new_domain, self.data)

        for i in range(len(new_data)):
            new_data[i, new_data.domain["data_out"]] = ""
        self.data = new_data

    def send_pointer(self):
        """Send a pointer to the current class for the loop."""
        pointer = str(id(self))
        self.Outputs.out_pointer.send(pointer)

if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    obj = LoopStartWidget()
    obj.show()
    app.exec_()
