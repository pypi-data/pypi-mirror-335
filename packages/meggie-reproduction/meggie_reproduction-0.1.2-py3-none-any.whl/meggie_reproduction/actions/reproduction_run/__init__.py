from meggie.mainwindow.dynamic import Action

from meggie_reproduction.actions.reproduction_run.dialogs.runActionsDialogMain import (
    RunActionsDialog,
)


class ReproductionRun(Action):
    """Applies action logs to subjects."""

    def run(self, params={}):
        run_actions_dialog = RunActionsDialog(self.window, self.experiment)
        run_actions_dialog.show()
