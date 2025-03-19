# This code is part of Tergite
#
# (C) Copyright Miroslav Dobsicek 2020, 2021
# (C) Copyright Axel Andersson 2022
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
#
# This code was refactored from the original on 22nd September, 2023 by Martin Ahindura
"""Defines the asynchronous job that executes the experiments."""
import logging
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import requests
from qiskit.providers import JobV1
from qiskit.providers.jobstatus import JOB_FINAL_STATES, JobStatus
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData

from tergite.qiskit.deprecated.qobj import PulseQobj, QasmQobj

from .serialization import iqx_rle

if TYPE_CHECKING:
    from tergite.qiskit.providers.provider import Provider

    from .backend import TergiteBackend

STATUS_MAP = {
    "REGISTERING": JobStatus.QUEUED,
    "DONE": JobStatus.DONE,
    # TODO: unimplemented status codes
    "INITIALIZING": JobStatus.INITIALIZING,
    "VALIDATING": JobStatus.VALIDATING,
    "RUNNING": JobStatus.RUNNING,
    "CANCELLED": JobStatus.CANCELLED,
    "ERROR": JobStatus.ERROR,
}
_JOB_FINAL_OR_INITIAL_STATES = (*JOB_FINAL_STATES, JobStatus.INITIALIZING)


class Job(JobV1):
    """A representation of the asynchronous job that handles experiments on a backend"""

    def __init__(
        self,
        *,
        backend: "TergiteBackend",
        job_id: str,
        payload: Optional[Union[QasmQobj, PulseQobj]] = None,
        upload_url: Optional[str] = None,
        remote_data: Optional[Dict[str, Any]] = None,
        logfile: Optional[Path] = None,
        status: JobStatus = JobStatus.INITIALIZING,
        download_url: Optional[str] = None,
        calibration_date: Optional[str] = None,
        **kwargs,
    ):
        """Initializes the job instance for the given backend

        Args:
            backend: the backed where the job is to run
            job_id: the unique id of the job
            upload_url: URL where the jobs will be uploaded
            payload: the qobj representing the experiments
            remote_data: the job data from the remote API
            logfile: the HDF5 logfile for this job
            status: the JobStatus of the current job; defaults to `JobStatus.INITIALIZING`
            download_url: the URL to download the results logfile from
            calibration_date: the last_calibrated timestamp of the backend when this job was compiled
            kwargs: extra key-word arguments to add to the job's metadata
        """
        super().__init__(
            backend=backend, job_id=job_id, upload_url=upload_url, **kwargs
        )
        self.payload = payload
        self.upload_url = upload_url
        self._remote_data = remote_data
        self._status = status
        self._logfile = logfile
        self._provider: Provider = backend.provider
        self._download_url = download_url
        self._calibration_date = calibration_date
        self._result: Optional[Result] = None

    @property
    def _is_in_final_state(self):
        """Whether this job has reached the end of the line or not

        It returns True if the job status is in `CANCELLED`, `ERROR`, `DONE`
        """
        try:
            return self._status in JOB_FINAL_STATES
        except RuntimeError:
            return False

    @property
    def remote_data(self) -> Optional[Dict[str, Any]]:
        """The representation of the job in the remote API"""
        if not self._is_in_final_state:
            self._remote_data = self._provider.get_remote_job_data(self.job_id())

        return self._remote_data

    def status(self) -> JobStatus:
        if not self._is_in_final_state:
            try:
                self._status = STATUS_MAP[self.remote_data["status"]]
            except (KeyError, AttributeError):
                pass

        return self._status

    def submit(self) -> requests.Response:
        """Submit the job to the backend for execution.

        Returns:
            requests.Response: the response of the API after submitting the job
        """
        if self._status != JobStatus.INITIALIZING:
            raise ValueError("This job was already submitted")

        if self.upload_url is None:
            raise ValueError("This job is not submittable. It lacks an upload_url")

        if isinstance(self.payload, QasmQobj):
            job_entry = {
                "job_id": self.job_id(),
                "type": "script",  # ?
                "name": "qasm_dummy_job",
                "params": {"qobj": self.payload.to_dict()},
                "post_processing": "process_qiskit_qasm_runner_qasm_dummy_job",
            }
        elif isinstance(self.payload, PulseQobj):
            payload = _compress_qobj_dict(self.payload.to_dict())
            job_entry = {
                "job_id": self.job_id(),
                "type": "script",  # ?
                "name": "pulse_schedule",
                "params": {"qobj": payload},
            }
        else:
            raise RuntimeError(f"Unprocessable payload type: {type(self.payload)}")

        return self._provider.send_job_file(url=self.upload_url, job_data=job_entry)

    @property
    def download_url(self) -> Optional[str]:
        """The download_url of this job when it is completed

        Raises:
            RuntimeError: Failed to GET download URL of job: {job_id}. Status: {JobStatus}
        """
        if self._download_url is None and self.status() in JOB_FINAL_STATES:
            try:
                self._download_url = self.remote_data["download_url"]
            except KeyError:
                raise RuntimeError(
                    f"Failed to GET download URL of job: {self.job_id()}. Status: {self.status()}"
                )

        return self._download_url

    @property
    def logfile(self) -> Optional[Path]:
        """The path to the logfile of this job when it is completed"""
        if self._logfile is None and self.status() in JOB_FINAL_STATES:
            if self.download_url:
                self._logfile = self._provider.download_job_logfile(
                    self.job_id(), url=self.download_url
                )

        return self._logfile

    def cancel(self):
        # TODO: This can be implemented server side with stoppable threads.
        print("Job.cancel() is not implemented.")

    def result(self) -> Optional[Result]:
        """Retrieves the outcome of this job when it is completed.

        It returns None if the job has not yet completed

        Returns:
            Optional[qiskit.result.result.Result]: the outcome of this job
                if it has completed

        Raises:
            RuntimeError: failed to GET memory of job: {job_id}
            RuntimeError: unexpected number of results; expected {num}, got: {num}
        """
        status = self.status()
        if status not in JOB_FINAL_STATES:
            logging.info(f"Job {self.job_id()} is not DONE. Status: {status}.")
            return

        if self._result is None:
            backend: TergiteBackend = self.backend()

            try:
                memory = self.remote_data["result"]["memory"]
            except (KeyError, AttributeError):
                raise RuntimeError(f"failed to GET memory of job: {self.job_id()}")

            # Sanity check
            if len(memory) != len(self.payload.experiments):
                raise RuntimeError(
                    f"unexpected number of results;"
                    f"expected {len(self.payload.experiments)}, got: {len(memory)}"
                )

            self._result = Result(
                backend_name=backend.name,
                backend_version=backend.backend_version,
                qobj_id=self.payload.qobj_id,
                job_id=self.job_id(),
                success=True,
                results=[
                    ExperimentResult(
                        header=self.payload.experiments[idx].header,
                        shots=self.payload.config.shots,
                        success=True,
                        data=ExperimentResultData(
                            counts=dict(Counter(v)),
                            memory=v,
                        ),
                    )
                    for idx, v in enumerate(memory)
                ],
            )

        return self._result

    def __repr__(self):
        kwargs = [f"{k}={repr(v)}" for k, v in self.__dict__.items()]
        kwargs_str = ",\n".join(kwargs)
        return f"{self.__class__.__name__}({kwargs_str})"

    def __eq__(self, other):
        if not isinstance(other, Job):
            return False

        for k, v in self.__dict__.items():
            other_v = getattr(other, k, None)
            if other_v != v:
                return False

        return True


def _compress_qobj_dict(qobj_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a compressed dictionary representation of the qobj dict

    In order to reduce the bandwidth taken up be the qobject
    dict, we do a few things with the data which will be reversed
    at the backend

    Note that this compression is in-place

    Args:
        qobj_dict: the dict of the PulseQobj to compress

    Returns:
        A compressed dict of the qobj
    """
    # In-place RLE pulse library for compression
    for pulse in qobj_dict["config"]["pulse_library"]:
        pulse["samples"] = iqx_rle(pulse["samples"])

    return qobj_dict
