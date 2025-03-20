import ctypes
import os
import sys
import Orange.data
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Input, Output, OWWidget


class EndLoopWidget(OWWidget):
    name = "End Loop"
    description = "Widget to end a loop based on a predefined condition."
    icon = "icons/endloop.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/endloop.png"

    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owendloop.ui")
    want_control_area = False
    priority = 1011

    class Inputs:
        in_data = Input("Data In", Orange.data.Table)
        in_pointer = Input("End of the Loop Do-While", str, auto_summary=False)

    class Outputs:
        out_data = Output("Data Out", Orange.data.Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.in_pointer = None

    @Inputs.in_data
    def set_data(self, data):
        if data is None:
            print("No data received in the end loop.")
            return
        self.error("")
        if self.in_pointer is None:
            return

        if data is not None:

            self.data = data
            # Check if the number of lines has changed
            if self.get_nb_line() != self.get_nb_line_from_start():
                self.error("Error! You can't change the number of lines in this version!")
                return

            table_representation = self.give_args_to_input()
            self.process_data_based_on_iter(table_representation)
            self.check_loop_condition(table_representation)


        else:
            print("No data received.")
            self.data = None

    @Inputs.in_pointer
    def set_pointer(self, pointer):
        self.in_pointer = int(pointer) if pointer else None

    def get_column_name_and_type_from_start(self):
        if self.in_pointer is not None:
            result = ctypes.cast(int(self.in_pointer), ctypes.py_object).value.get_column_name_and_type()
        return result

    def get_nb_line_from_start(self):
        result = 0
        if self.in_pointer is not None:
            result = ctypes.cast(int(self.in_pointer), ctypes.py_object).value.get_nb_line()
        return result

    def get_nb_line(self):
        # Return the number of lines to compare with another widget
        if self.data is None:
            return 0
        return len(self.data)

    def get_column_name_and_type(self):
        # Return the name and type of 'data_in' to verify if they are the same
        if self.data is None:
            return [[], []]
        column_names = []
        column_types = []
        for element in self.data.domain:
            column_names.append(str(element))
            column_types.append(str(type(element)))
        return column_names, column_types


    def give_args_to_input(self):
        # pour toutes les colonnes de data_in -> si la colonne n 'est pas dans in loop continue
        col_names,col_types=self.get_column_name_and_type()
        col_names_start_loop,col_types_start_loop=(self.get_column_name_and_type_from_start())

        nb_maj=0
        table_representation = []
        for i in range(len(col_names)):
            for j in range(len(col_names_start_loop)):
                if col_names[i]!=col_names_start_loop[j]:
                    continue
                if col_types[i] != col_types_start_loop[j]:
                    self.error("col type change "+col_types_start_loop[j]+"->"+col_types[i]+" ("+col_names[i])+")"
                    return 1


                column_name = col_names[i]
                column_type = col_types[i]

                # Extract value form column
                variable = self.data.domain[column_name]
                print(variable)
                column_values = [row[variable].value for row in self.data]

                table_representation.append({
                    "name": column_name,
                    "type": column_type,
                    "values": column_values
                })


        iter = [row['iter'] for row in self.data]
        table_representation.append({
            "name": 'iter',
            "type": "ContinuousVariable",
            "values": iter
        })
        return table_representation


    def process_data_based_on_iter(self, table_representation):
        """Update 'data_in' and 'data_out' in table_representation based on the value of 'iter'."""
        # find column 'iter', 'data_in' et 'data_out'
        iter_column = next((col for col in table_representation if col['name'] == 'iter'), None)
        data_in_column = next((col for col in table_representation if col['name'] == 'data_in'), None)
        data_out_column = next((col for col in table_representation if col['name'] == 'data_out'), None)

        if iter_column is None or data_in_column is None or data_out_column is None:
            self.error("Required columns 'iter', 'data_in', or 'data_out' not found in table_representation.")
            return

        iter_values = iter_column['values']
        data_in_values = data_in_column['values']
        data_out_values = data_out_column['values']

        for i in range(len(iter_values)):
            iter_value = iter_values[i]
            # Convertir iter_value en entier 0 ou 1
            if isinstance(iter_value, (float, int)):
                iter_value = int(bool(iter_value))
            elif isinstance(iter_value, str):
                iter_value = int(iter_value.lower() == 'true' or iter_value == '1')
            else:
                iter_value = 0  # Par défaut à 0

            data_in_value = str(data_in_values[i])
            data_out_value = str(data_out_values[i])

            if iter_value == 1:
                print(f"Transferring row {i} to 'data_out'.")
                if data_out_value in ("", "0.0", "?"):
                    data_out_values[i] = data_in_value
                data_in_values[i] = ""  # Effacer 'data_in'
            # Si iter_value == 0, ne rien faire

    def check_loop_condition(self, table_representation):
        """Check whether the loop should continue or stop."""
        all_iters = []
        for row in self.data:
            iter_value = row[self.data.domain["iter"]]
            iter_value = int(bool(iter_value)) if isinstance(iter_value, (float, int)) else int(iter_value.lower() == "true") if isinstance(iter_value, str) else 0
            all_iters.append(iter_value)
        # delete 'iter' from table_representation
        table_representation = [col for col in table_representation if col['name'] != 'iter']

        if all(value == 1 for value in all_iters):
            print("All rows have iter == 1. Sending final data.")
            final_data = self.clean_final_data(self.data, table_representation)
            self.Outputs.out_data.send(final_data)
        else:
            print("Some rows have iter == 0. Restarting the loop.")
            self.data = table_representation
            if self.in_pointer is not None:
                start_widget = ctypes.cast(int(self.in_pointer), ctypes.py_object).value
                if hasattr(start_widget, 'set_data'):
                    start_widget.set_data(self.data)

    import datetime
    import numpy as np
    import Orange.data

    def convert_value(self, value, var):
        """
        Convert 'value' to the appropriate type for the Orange variable 'var'.

        Parameters
        ----------
        value : Any (str, float, None, etc.)
            The raw value that needs to be converted according to 'var' type.
        var : Orange.data.Variable
            The Orange variable to which we want to convert 'value'.
            It can be ContinuousVariable, StringVariable, DiscreteVariable, TimeVariable, etc.

        Returns
        -------
        converted_value : float | str | int | np.nan
            The value converted according to the type of 'var'.
            For instance:
              - float('nan') if the value cannot be converted or is missing,
              - a float for continuous variables,
              - a string for string variables,
              - an integer index for discrete variables, etc.
        """

        # 1) Handle missing or undefined values (None, '?', empty string, etc.)
        if value is None or value == "?" or str(value).strip() == "":
            if isinstance(var, Orange.data.ContinuousVariable):
                # For continuous variables, assign missing to NaN
                return float('nan')
            elif isinstance(var, Orange.data.StringVariable):
                # For string variables, return an empty string
                return ""
            elif isinstance(var, Orange.data.DiscreteVariable):
                # For discrete variables, if "unknown" is in var.values, use its index;
                # otherwise return np.nan or another default index
                if "unknown" in var.values:
                    return var.values.index("unknown")
                else:
                    return np.nan
            elif isinstance(var, Orange.data.TimeVariable):
                # For time variables, return NaN for missing
                return float('nan')
            else:
                # For any other type or unrecognized cases, return the raw value
                return value

        # 2) Conversion logic based on the variable's type

        # ContinuousVariable -> float
        if isinstance(var, Orange.data.ContinuousVariable):
            try:
                return float(value)
            except Exception:
                # If conversion fails, return NaN
                return float('nan')

        # StringVariable -> string
        elif isinstance(var, Orange.data.StringVariable):
            return str(value)

        # DiscreteVariable -> index of the modality in var.values
        elif isinstance(var, Orange.data.DiscreteVariable):
            if value in var.values:
                return var.values.index(value)
            else:
                # If the value is not in the modality list, handle it as unknown (NaN)
                return np.nan

        # TimeVariable -> parse and convert to timestamp (float)
        elif isinstance(var, Orange.data.TimeVariable):
            # Example: parse the string as ISO8601 date/time
            try:
                dt = datetime.datetime.fromisoformat(str(value))
                return dt.timestamp()
            except Exception:
                return float('nan')

        # 3) If you have other types to handle or if the type is unknown, return the raw value
        else:
            return value

    def clean_final_data(self, data, table_representation):
        """Clean the data by replacing values from table_representation, removing 'iter' and 'data_out',
        and updating 'data_in' with values from 'data_out'."""

        # Step 1 : Create list variables (attributs and méta) without 'iter' and 'data_out'
        variables = [var for var in data.domain.variables if var.name not in ('iter', 'data_out')]
        metas = [meta for meta in data.domain.metas if meta.name not in ('iter', 'data_out')]

        # Step 2 : Creat a new domain
        new_domain = Orange.data.Domain(variables, metas=metas)

        # Step 3 : Creat dict with the value from table_representation
        col_values = {}
        for col in table_representation:
            col_name = col['name']
            col_values[col_name] = col['values']

        # Setp 4 : buile row by row data
        num_rows = len(next(iter(col_values.values())))
        data_rows = []
        for i in range(num_rows):
            row_attrs = []
            row_metas = []
            # for attribut
            for var in variables:
                var_name = var.name
                # Replace
                if var_name == 'data_in' and 'data_out' in col_values:
                    value = col_values['data_out'][i]
                else:
                    value = col_values.get(var_name, [])[i]
                # Put type
                value = self.convert_value(value, var)
                row_attrs.append(value)
            # For meta
            for var in metas:
                var_name = var.name
                if var_name == 'data_in' and 'data_out' in col_values:
                    value = col_values['data_out'][i]
                else:
                    value = col_values.get(var_name, [])[i]
                row_metas.append(value)
            data_rows.append(row_attrs + row_metas)

        # Step 5 : Build Orange data table
        final_data = Orange.data.Table(new_domain, data_rows)

        return final_data


if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    obj = EndLoopWidget()
    obj.show()
    app.exec_()
