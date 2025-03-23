"""Contains implementation for epochs plot"""

from meggie.utilities.messaging import exc_messagebox
from meggie.mainwindow.dynamic import Action


class PlotEpochs(Action):
    """Plots all epochs from all channels."""

    def run(self, params={}):

        try:
            selected_name = self.data["outputs"]["epochs"][0]
        except IndexError:
            return

        subject = self.experiment.active_subject
        try:
            self.handler(subject, {"name": selected_name})
        except Exception as exc:
            exc_messagebox(self.window, exc)

    def handler(self, subject, params):
        epochs = subject.epochs.get(params["name"])
        mne_epochs = epochs.content
        mne_epochs.plot()
