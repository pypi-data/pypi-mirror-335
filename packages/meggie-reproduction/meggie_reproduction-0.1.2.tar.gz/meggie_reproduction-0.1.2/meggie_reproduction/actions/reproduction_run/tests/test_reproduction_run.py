import os
import time

from meggie.utilities.testing import BaseTestAction
from meggie.utilities.testing import create_evoked_conditions_experiment

from meggie_reproduction.actions.reproduction_run import ReproductionRun
from meggie_reproduction.actions.reproduction_run.dialogs.runActionsDialogMain import (
    RunActionsDialog,
)


class TestReproductionRunTest(BaseTestAction):
    def setup_experiment(self):

        self.experiment = create_evoked_conditions_experiment(
            self.dirpath, "test_experiment", n_subjects=1
        )
        self.experiment.activate_subject("sample_01-raw")

        test_dir = os.path.dirname(os.path.abspath(__file__))
        self.actions_path = os.path.join(test_dir, "actions.json")

    def test_reproduction_run(self):

        self.run_action(
            action_name="reproduction_run",
            handler=ReproductionRun,
            data={},
            patch_paths=[],
        )
        dialog = self.find_dialog(RunActionsDialog)
        dialog.ui.lineEditSourceCurrentSelection.setText(self.actions_path)

        # make sure we got some actions
        time.sleep(1)
        assert len(dialog.actions_available) > 0

        for idx, action_id in enumerate(dialog.actions_available):
            print(f"Running action: {action_id}")
            dialog.ui.listWidgetAvailable.setCurrentRow(idx)
            dialog.on_pushButtonActionsRun_clicked(True)

        # this action log creates an evoked object, ensure its there
        assert len(self.experiment.active_subject.evoked) > 0
