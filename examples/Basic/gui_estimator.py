#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use.

Run the program by changing to the directory containing this file and calling:

python gui.py

"""

import sys
import random
from time import sleep

from datetime import datetime, timedelta

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)

    def execute(self):
        log.info("Starting to generate numbers")
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Random Number': random.random()
            }
            log.debug("Produced numbers: %s" % data)
            self.emit('results', data)
            self.emit('progress', 100 * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def get_estimates(self, sequence_length=None, sequence=None):
        """ Function that returns estimates for the EstimatorWidget. If this function
        is implemented (and does not return a NotImplementedError) the widget is
        automatically activated.

        The function is expected to return an int or float, or a list of tuples. If an int or
        float is returned, it should represent the duration in seconds.If a list of
        tuples is returned, each tuple containing two strings, a label and the estimate
        itself:
        estimates = [
            ("label 1", "estimate 1"),
            ("label 2", "estimate 2"),
        ]
        The length of the number of estimates is not limited but has to remain unchanged after
        initialisation. Note that also the label can be altered after initialisation.

        The keyword arguments `sequence_length` and `sequence` are optional and return
        (if asked for) the length of the current sequence (of the `SequencerWidget`) or
        the full sequence.

        """
        duration = self.iterations * self.delay

        """
        A simple implementation of the get_estimates function immediately returns the duration
        in seconds.
        """
        # return duration

        estimates = list()

        estimates.append(("Duration", "%d s" % int(duration)))
        estimates.append(("Number of lines", "%d" % int(self.iterations)))

        estimates.append(("Sequence length", str(sequence_length)))

        estimates.append(('Measurement finished at', str(datetime.now() + timedelta(
            seconds=duration))[:-7]))
        estimates.append(('Sequence finished at', str(datetime.now() + timedelta(
            seconds=duration * sequence_length))[:-7]))

        return estimates

    def shutdown(self):
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=TestProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number',
            sequencer=True,
            sequence_file="gui_sequencer_example_sequence.txt"
        )
        self.setWindowTitle('GUI Example')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
