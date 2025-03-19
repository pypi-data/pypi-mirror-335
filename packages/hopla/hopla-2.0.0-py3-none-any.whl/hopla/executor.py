##########################################################################
# Hopla - Copyright (C) AGrigis, 2015 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Contains job execution functions.
"""

import abc
import time
from tqdm import tqdm
from pathlib import Path
from .pbs import DelayedPbsJob, PbsInfoWatcher


class Executor(abc.ABC):
    """ Base job executor.

    Parameters
    ----------
    folder: Path/str
        folder for storing job submission/output and logs.
    queue: str
        the name of the queue where the jobs will be submited.
    name: str, default 'hopla'
        the name of the submitted jobs.
    memory: float , default 2
        the memory allocated to each job (in GB).
    walltime: int default 72
        the walltime used for each job (in hours).
    n_cpus: int, default 1
        the number of cores allocated for each job.
    n_gpus: int, default 0
        the number of GPUs allocated for each job.

    Examples
    --------
    >>> import hopla
    >>> executor = hopla.Executor(folder="/tmp/hopla", queue="Nspin_long")
    >>> jobs = [executor.submit("sleep", k) for k in range(1, 11)]
    >>> executor(max_jobs=2)
    >>> print(executor.report)
    """
    _delay_s = 60
    _counter = 0
    _start = time.time()
    _job_class = DelayedPbsJob
    _watcher_class = PbsInfoWatcher

    def __init__(self, folder, queue, name="hopla", memory=2, walltime=72,
                 n_cpus=1, n_gpus=0):
        self.watcher = self._watcher_class(self._delay_s)
        self.folder = Path(folder).expanduser().absolute()
        self.parameters = {
            "name": name,
            "queue": queue, "memory": memory, "walltime": walltime,
            "ncpus": n_cpus, "ngpus": n_gpus
        }
        self._delayed_jobs = []

    def __call__(self, max_jobs=300, debug=False):
        """ Run jobs controlling the maximum number of concurrent submissions.

        Parameters
        ----------
        max_jobs: int, default 300
            the maximum number of concurrent submissions.
        debug: bool, default False
            optionaly print job info at each refresh.
        """
        _start = 0
        pbar = tqdm(total=self.n_jobs, desc="QSUB")
        while (self.n_waiting_jobs != 0 or
               not all([job.done for job in self._delayed_jobs])):
            if debug:
                print(self.status)
                print(self._delayed_jobs)
            if self.n_waiting_jobs != 0 and self.n_running_jobs < max_jobs:
                _delta = max_jobs - self.n_running_jobs
                _stop = _start + _delta
                for job in self._delayed_jobs[_start:_stop]:
                    assert job.status == "NOTSTARTED"
                    job.start()
                _start = _stop
                pbar.update(_delta)
            time.sleep(self._delay_s)
        self.watcher.update()

    def submit(self, script, *args, **kwargs):
        """ Create a delayed job.

        Parameters
        ----------
        script: Path/str
            script to execute.
        *args: any positional argument of the script.
        **kwargs: any named argument of the script.

        Returns
        -------
        job: DelayedJob
            a job instance.
        """
        self._counter += 1
        job = self._job_class(DelayedSubmission(script, *args, **kwargs), self,
                              self._counter)
        self._delayed_jobs.append(job)
        return job

    @property
    def status(self):
        """ Display current status.
        """
        message = ["-" * 40]
        message += [f"{self.__class__.__name__}<time="
                    f"{time.time() - self._start}>"]
        message += [f"- jobs: {self.n_jobs}"]
        message += [f"- done: {self.n_done_jobs}"]
        message += [f"- running: {self.n_running_jobs}"]
        message += [f"- waiting: {self.n_waiting_jobs}"]
        return "\n".join(message)

    @property
    def report(self):
        """ Generate a general report for all jobs.
        """
        message = [job.report for job in self._delayed_jobs]
        return "\n".join(message)

    @property
    def n_jobs(self):
        """ Get the number of stacked jobs.
        """
        return len(self._delayed_jobs)

    @property
    def n_done_jobs(self):
        """ Get the number of finished jobs.
        """
        return sum([job.done for job in self._delayed_jobs])

    @property
    def n_waiting_jobs(self):
        """ Get the number of waiting jobs.
        """
        return sum([job.status == "NOTSTARTED" for job in self._delayed_jobs])

    @property
    def n_running_jobs(self):
        """ Get the number of running jobs.
        """
        return self.n_jobs - self.n_done_jobs - self.n_waiting_jobs


class DelayedSubmission:
    """ Object for specifying the submit parameters for further processing.
    """
    def __init__(self, script, *args, **kwargs):
        self.script = script
        self.args = args
        self.kwargs = kwargs

    @property
    def command(self):
        """ Return the command to execute.
        """
        command = [self.script]
        command += [str(e) for e in self.args]
        command += [f"{-key} {val}" for key, val in self.kwargs.items()]
        return " ".join(command)
