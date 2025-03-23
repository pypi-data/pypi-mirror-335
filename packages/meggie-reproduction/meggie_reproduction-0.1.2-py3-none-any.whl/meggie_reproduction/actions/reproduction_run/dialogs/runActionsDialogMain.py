"""Contains a class for logic of the run actions dialog."""

import json
import importlib

from PyQt5 import QtWidgets

from meggie_reproduction.actions.reproduction_run.dialogs.runActionsDialogUi import (
    Ui_RunActionsDialog,
)

from meggie.mainwindow.dynamic import find_all_action_specs

from meggie.utilities.messaging import exc_messagebox
from meggie.utilities.messaging import messagebox
from meggie.utilities.filemanager import homepath
from meggie.utilities.serialization import deserialize_dict


class RunActionsDialog(QtWidgets.QDialog):
    """Contains logic for the run actions dialog."""

    def __init__(self, parent, experiment):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_RunActionsDialog()
        self.ui.setupUi(self)

        self.experiment = experiment
        self.parent = parent

        self.action_log = None
        self.action_specs = find_all_action_specs()
        self.current_subject = None

        self.actions_available = []
        self.actions_done = []

        self.ui.lineEditSourceCurrentSelection.setText("")
        self.ui.groupBoxSubject.setEnabled(False)
        self.ui.comboBoxSubject.clear()
        self.ui.listWidgetAvailable.clear()
        self.ui.listWidgetDone.clear()
        self.ui.textBrowserActionsInfo.setPlainText("")
        self.ui.groupBoxActions.setEnabled(False)

        # Add handler for action log change
        self.ui.lineEditSourceCurrentSelection.textChanged.connect(
            self.on_action_log_changed
        )

        # Add handler for subject change
        self.ui.comboBoxSubject.currentTextChanged.connect(self.on_subject_changed)

        # Add handler for action selection
        self.ui.listWidgetAvailable.currentItemChanged.connect(
            self.on_action_item_changed
        )

    def on_action_log_changed(self, value):
        if not value:
            return

        try:
            with open(value) as f:
                self.action_log = json.load(f)
        except Exception as exc:
            exc_messagebox(self, exc)

        if not self.action_log:
            messagebox(self, "The selected action log seems empty.")
            return

        self.ui.groupBoxSubject.setEnabled(True)
        self.ui.comboBoxSubject.addItems(sorted(self.action_log.keys()))

    def on_subject_changed(self, value):
        if not value:
            return

        if not self.actions:
            return

        # sanity check to not update if subject did not really change
        if self.current_subject == value:
            return
        self.current_subject = value

        # get installed actions
        installed_actions = [spec[2]["id"] for spec in self.action_specs.values()]

        # ensure all actions are available in the installation
        for action in self.action_log[value]:
            if action["id"] not in installed_actions:
                messagebox(
                    self, f"The log contains {action['id']} that is not installed."
                )
                return

        # update available actions
        self.actions_available = []
        self.ui.listWidgetAvailable.clear()
        for action in self.action_log[value]:

            # get the action spec
            action_spec = self.action_specs.get(action["id"])
            if action_spec:
                self.actions_available.append(action["id"])
                self.ui.listWidgetAvailable.addItem(
                    f"{action_spec[2]['name']} ({action['desc']})"
                )

        self.ui.groupBoxActions.setEnabled(True)

    def on_action_item_changed(self, value):
        action_idx = self.ui.listWidgetAvailable.indexFromItem(value).row()
        action = self.action_log[self.current_subject][action_idx]
        self.ui.textBrowserActionsInfo.setPlainText(json.dumps(action, indent=2))

    def on_subject_action_finished(self, action_id, subject_name):

        if subject_name != self.experiment.active_subject.name:
            return

        # Add item to the 'done' box
        _, _, action_spec = self.action_specs[action_id]
        self.actions_done.append(action_id)
        self.ui.listWidgetDone.addItem(f"{action_spec['name']}")

    def on_pushButtonActionsRun_clicked(self, checked=None):
        if checked is None:
            return

        selected_item = self.ui.listWidgetAvailable.currentItem()

        action_idx = self.ui.listWidgetAvailable.indexFromItem(selected_item).row()
        action = self.action_log[self.current_subject][action_idx]

        version = action.get("version")
        if version != 1:
            messagebox(self, "The action version is not supported, needed 1.")
            return

        params = action.get("params")
        if params is None:
            messagebox(self, "Action params were not found.")
            return

        # get correctly typed params
        params = deserialize_dict(params)

        data = action.get("data")
        if data is None:
            messagebox(self, "Action data was not found.")
            return

        # find the corresponding callable
        source, package, action_spec = self.action_specs[action["id"]]
        module = importlib.import_module(".".join([source, "actions", package]))
        entry = action_spec["entry"]
        action_class = getattr(module, entry)

        # instantiate an object but do not call the run
        try:
            action_obj = action_class(
                self.experiment,
                data,
                self.parent,
                action_spec,
                subject_action_callback=self.on_subject_action_finished,
            )
        except Exception as exc:
            exc_messagebox(self, exc)
            return

        # try to find out the subject_action function
        method_name = None
        for attr_name in dir(action_obj):
            attr = getattr(action_obj, attr_name)
            if callable(attr) and hasattr(attr, "_is_subject_action"):
                method_name = attr_name
                break
        else:
            messagebox(self, "It seems this action cannot be run without a dialog.")
            return

        # .. and call the subject_action
        subject = self.experiment.active_subject
        try:
            getattr(action_obj, method_name)(subject, params)
        except Exception as exc:
            exc_messagebox(self, exc)

    def on_pushButtonActionsRunDialog_clicked(self, checked=None):
        if checked is None:
            return

        selected_item = self.ui.listWidgetAvailable.currentItem()

        action_idx = self.ui.listWidgetAvailable.indexFromItem(selected_item).row()
        action = self.action_log[self.current_subject][action_idx]

        version = action.get("version")
        if version != 1:
            messagebox(self, "The action version is not supported, needed 1.")
            return

        params = action.get("params")
        if params is None:
            messagebox(self, "Action params were not found.")
            return

        # get correctly typed params
        params = deserialize_dict(params)

        data = action.get("data")
        if data is None:
            messagebox(self, "Action data was not found.")
            return

        # find the corresponding callable
        source, package, action_spec = self.action_specs[action["id"]]
        module = importlib.import_module(".".join([source, "actions", package]))
        entry = action_spec["entry"]
        action_class = getattr(module, entry)

        # Open the widget with default params (if supported)
        try:
            action_obj = action_class(
                self.experiment,
                data,
                self.parent,
                action_spec,
                subject_action_callback=self.on_subject_action_finished,
            )
            action_obj.run(params)
        except Exception as exc:
            exc_messagebox(self, exc)
            return

    def on_pushButtonSourceBrowse_clicked(self, checked=None):
        if checked is None:
            return

        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Action Log", homepath(), "JSON Files (*.json);;All Files (*)"
        )
        if not fname:
            return

        self.ui.lineEditSourceCurrentSelection.setText(str(fname))

    def on_pushButtonClose_clicked(self, checked=None):
        if checked is None:
            return

        self.close()

    def closeEvent(self, event):
        """Initialize the ui when the dialog is closed."""
        self.parent.initialize_ui()
        event.accept()
