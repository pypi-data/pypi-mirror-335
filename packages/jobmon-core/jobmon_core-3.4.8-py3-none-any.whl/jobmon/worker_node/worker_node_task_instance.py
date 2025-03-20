"""The Task Instance Object once it has been submitted to run on a worker node."""

import asyncio
import logging
import logging.config
import os
import signal
import socket
import sys
from time import time
from typing import Dict, Optional, TextIO

from jobmon.core.cluster_protocol import ClusterWorkerNode
from jobmon.core.configuration import JobmonConfig
from jobmon.core.constants import TaskInstanceStatus
from jobmon.core.exceptions import ReturnCodes, TransitionError
from jobmon.core.requester import Requester
from jobmon.core.serializers import SerializeTaskInstance

logger = logging.getLogger(__name__)


class WorkerNodeTaskInstance:
    """The Task Instance object once it has been submitted to run on a worker node."""

    def __init__(
        self,
        cluster_interface: ClusterWorkerNode,
        task_instance_id: int,
        task_instance_heartbeat_interval: Optional[int] = None,
        heartbeat_report_by_buffer: Optional[float] = None,
        command_interrupt_timeout: Optional[int] = None,
        requester: Optional[Requester] = None,
    ) -> None:
        """A mechanism whereby a running task_instance can communicate back to the JSM.

         Logs its status, errors, usage details, etc.

        Args:
            cluster_interface: interface that gathers executor info in the execution_wrapper.
            task_instance_id: the id of the TaskInstance that is reporting back.
            task_instance_heartbeat_interval: how ofter to log a report by with the db
            heartbeat_report_by_buffer: multiplier for report by date in case we miss a few.
            command_interrupt_timeout: the amount of time to wait for the child process to
                terminate.
            requester: communicate with the flask services.
        """
        # identity attributes
        self._task_instance_id = task_instance_id

        # service API
        if requester is None:
            requester = Requester.from_defaults()
        self.requester = requester

        # cluster API
        self.cluster_interface = cluster_interface

        # get distributor id from executor
        self._distributor_id = self.cluster_interface.distributor_id

        # config
        config = JobmonConfig()
        if task_instance_heartbeat_interval is None:
            self._task_instance_heartbeat_interval = config.get_int(
                "heartbeat", "task_instance_interval"
            )
        else:
            self._task_instance_heartbeat_interval = task_instance_heartbeat_interval
        if heartbeat_report_by_buffer is None:
            self._heartbeat_report_by_buffer = config.get_float(
                "heartbeat", "report_by_buffer"
            )
        else:
            self._heartbeat_report_by_buffer = heartbeat_report_by_buffer
        if command_interrupt_timeout is None:
            self._command_interrupt_timeout = config.get_int(
                "worker_node", "command_interrupt_timeout"
            )
        else:
            self._command_interrupt_timeout = command_interrupt_timeout

        # attrs set by log running
        self._status: Optional[str] = None
        self._command: Optional[str] = None
        self._command_add_env: Optional[Dict[str, str]] = None
        self._stdout: Optional[str] = None
        self._stderr: Optional[str] = None

        # set last heartbeat
        self.last_heartbeat_time = time()

    @property
    def task_instance_id(self) -> int:
        """Returns a task instance ID if it's been bound."""
        if self._task_instance_id is None:
            raise AttributeError("Cannot access task_instance_id because it is None.")
        return self._task_instance_id

    @property
    def distributor_id(self) -> Optional[str]:
        """Executor id given from the executor it is being run on."""
        return self._distributor_id

    @property
    def nodename(self) -> Optional[str]:
        """Node it is being run on."""
        if not hasattr(self, "_nodename"):
            self._nodename = socket.getfqdn()
        return self._nodename

    @property
    def process_group_id(self) -> Optional[int]:
        """Process group to track parent and child processes."""
        if not hasattr(self, "_process_group_id"):
            self._process_group_id = os.getpid()
        return self._process_group_id

    @property
    def status(self) -> str:
        """Returns the last known status of the task instance."""
        if self._status is None:
            raise AttributeError(
                "Cannot access status until log_running() has been called."
            )
        return self._status

    @property
    def stdout(self) -> str:
        if self._stdout is None:
            raise AttributeError(
                "Cannot access stdout until log_running() has been called."
            )
        return self._stdout

    @property
    def stderr(self) -> str:
        if self._stderr is None:
            raise AttributeError(
                "Cannot access stderr until log_running() has been called."
            )
        return self._stderr

    @property
    def command(self) -> str:
        """Returns the command this task instance will run."""
        if self._command is None:
            raise AttributeError(
                "Cannot access command until log_running() has been called."
            )
        return self._command

    @property
    def command_add_env(self) -> Dict[str, str]:
        """Returns the command this task instance will run."""
        if self._command_add_env is None:
            raise AttributeError(
                "Cannot access command_add_env until log_running() has been called."
            )
        return self._command_add_env

    @property
    def command_returncode(self) -> int:
        """Returns the exit code of the command that was run."""
        if not hasattr(self, "_proc_returncode"):
            raise AttributeError(
                "Cannot access command_returncode until run() has been called"
            )
        return self._proc_returncode

    @property
    def command_stdout(self) -> str:
        """Returns the last 10k characters of the commands stdout."""
        if not hasattr(self, "_proc_stdout"):
            raise AttributeError(
                "Cannot access command_stdout until run() has been called"
            )
        return self._proc_stdout

    @property
    def command_stderr(self) -> str:
        """Returns the last 10k characters of the commands stderr."""
        if not hasattr(self, "_proc_stderr"):
            raise AttributeError(
                "Cannot access command_stderr until run() has been called"
            )
        return self._proc_stderr

    def configure_logging(self) -> None:
        """Setup logging for the worker node. INFO level goes to standard out."""
        _DEFAULT_LOG_FORMAT = (
            "%(asctime)s [%(name)-12s] %(module)s %(levelname)-8s: %(message)s"
        )
        logging_config: Dict = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "default": {
                    "format": _DEFAULT_LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "jobmon.worker_node": {
                    "handlers": ["default"],
                    "propagate": False,
                    "level": "INFO",
                },
            },
        }
        logging.config.dictConfig(logging_config)

    def log_done(self) -> None:
        """Tell the JobStateManager that this task_instance is done."""
        logger.info(f"Logging done for task_instance {self.task_instance_id}")

        message = {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "stdout_log": self.command_stdout,
            "stderr_log": self.command_stderr,
            "nodename": self.nodename,
            "distributor_id": self.distributor_id,
        }

        app_route = f"/task_instance/{self.task_instance_id}/log_done"
        _, response = self.requester.send_request(
            app_route=app_route,
            message=message,
            request_type="post",
        )
        self._status = response["status"]
        if self.status != TaskInstanceStatus.DONE:
            raise TransitionError(
                f"TaskInstance {self.task_instance_id} failed because it could not transition "
                f"to {TaskInstanceStatus.DONE} status. Current status is {self.status}."
            )

    def log_error(self, error_state: str, description: str) -> None:
        """Tell the JobStateManager that this task_instance has errored."""
        logger.info(f"Logging error for task_instance {self.task_instance_id}")

        message = {
            "error_state": error_state,
            "error_description": description,
            "stdout_log": self.command_stdout,
            "stderr_log": self.command_stderr,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "nodename": self.nodename,
            "distributor_id": self.distributor_id,
        }

        app_route = f"/task_instance/{self.task_instance_id}/log_error_worker_node"
        _, response = self.requester.send_request(
            app_route=app_route,
            message=message,
            request_type="post",
        )
        self._status = response["status"]
        if self.status != error_state:
            raise TransitionError(
                f"TaskInstance {self.task_instance_id} failed because it could not transition "
                f"to {error_state} status. Current status is {self.status}."
            )

    def log_running(self) -> None:
        """Tell the JobStateManager that this task_instance is running.

        Update the report_by_date to be further in the future in case it gets reconciled
        immediately.
        """
        logger.info(f"Log running for task_instance {self.task_instance_id}")
        message = {
            "nodename": self.nodename,
            "process_group_id": str(self.process_group_id),
            "next_report_increment": (
                self._task_instance_heartbeat_interval
                * self._heartbeat_report_by_buffer
            ),
        }
        if self.distributor_id is not None:
            message["distributor_id"] = str(self.distributor_id)
        else:
            logger.info(
                "No distributor_id was found in the worker_node env at this time."
            )

        app_route = f"/task_instance/{self.task_instance_id}/log_running"
        _, response = self.requester.send_request(
            app_route=app_route,
            message=message,
            request_type="post",
        )

        kwargs = SerializeTaskInstance.kwargs_from_wire_worker_node(
            response["task_instance"]
        )
        self._status = kwargs.pop("status")
        self._command = kwargs.pop("command")
        task_name = kwargs.pop("name")
        self._stdout = self.cluster_interface.initialize_logfile(
            "stdout", kwargs.pop("stdout_dir"), task_name
        )
        self._stderr = self.cluster_interface.initialize_logfile(
            "stderr", kwargs.pop("stderr_dir"), task_name
        )
        self._command_add_env = {
            f"JOBMON_{k.upper()}": str(v) for k, v in kwargs.items()
        }
        self.last_heartbeat_time = time()
        if self.status != TaskInstanceStatus.RUNNING:
            raise TransitionError(
                f"TaskInstance {self.task_instance_id} failed because it could not transition "
                f"to {TaskInstanceStatus.RUNNING} status. Current status is {self.status}."
            )

    def log_report_by(self) -> None:
        """Log the heartbeat to show that the task instance is still alive."""
        logger.debug(f"Logging heartbeat for task_instance {self.task_instance_id}")
        message: Dict = {
            "next_report_increment": (
                self._task_instance_heartbeat_interval
                * self._heartbeat_report_by_buffer
            ),
            "stdout": self.stdout,
            "stderr": self.stderr,
        }
        if self.distributor_id is not None:
            message["distributor_id"] = str(self.distributor_id)
        else:
            logger.debug("No distributor_id was found in the sbatch env at this time")

        app_route = f"/task_instance/{self.task_instance_id}/log_report_by"
        _, response = self.requester.send_request(
            app_route=app_route,
            message=message,
            request_type="post",
        )

        self._status = response["status"]
        self.last_heartbeat_time = time()

        if self.status != TaskInstanceStatus.RUNNING:
            raise TransitionError(
                f"TaskInstance {self.task_instance_id} failed because it could not transition "
                f"to {TaskInstanceStatus.RUNNING} status. Current status is {self.status}."
            )

    def run(self) -> None:
        """This script executes on the target node and wraps the target application.

        Could be in any language, anything that can execute on linux. Similar to a stub or a
        container set ENV variables in case tasks need to access them.

        """
        # If it logs running and is not able to transition it raises TransitionError
        self.log_running()

        try:
            # run the command in a subprocess
            asyncio.run(self._run_cmd())

        # some other deployment unit transitioned task instance out of R state
        except RuntimeError as e:
            if isinstance(e.__cause__, TransitionError):
                msg = (
                    f"TaskInstance is in status '{self.status}'. Expected status 'R'."
                    f" Terminating command {self.command}."
                )
                logger.error(msg)

                # log an error with db if we are in K state
                if self.status == TaskInstanceStatus.KILL_SELF:
                    msg = (
                        f"Command: '{self.command}' got KILL_SELF event. Process shut down"
                        f" with exit code: '{self.command_returncode}'"
                    )
                    logger.error(msg)
                    self.log_error(TaskInstanceStatus.ERROR_FATAL, msg)

                # otherwise raise the error cause we are in trouble
                else:
                    raise e.__cause__
            else:
                raise

        # normal happy path
        else:
            if self.command_returncode == ReturnCodes.OK:
                logger.info(f"Command: {self.command}. Finished Successfully.")
                self.log_done()
            else:
                logger.info(
                    f"Command: {self.command} exited with signal {self.command_returncode}"
                )
                error_state, msg = self.cluster_interface.get_exit_info(
                    self.command_returncode, self.command_stderr
                )
                self.log_error(error_state, msg)

    def set_command_output(self, returncode: int, stdout: str, stderr: str) -> None:
        self._proc_returncode = returncode
        self._proc_stdout = stdout
        self._proc_stderr = stderr

    @staticmethod
    async def _communicate(
        async_stream: asyncio.StreamReader, output_stream: TextIO, chunk_size: int = 64
    ) -> str:
        mem_buffer = ""
        try:
            while True:
                # Read a chunk of data. If no data is returned, we've reached EOF.
                data_chunk = await async_stream.read(chunk_size)
                if not data_chunk:
                    break  # EOF reached

                # Attempt to decode and write the data chunk.
                try:
                    data_chunk_str = data_chunk.decode()
                    output_stream.write(data_chunk_str)
                    output_stream.flush()
                    mem_buffer += data_chunk_str
                    # Keep only the last 10k characters in memory.
                    mem_buffer = mem_buffer[-10000:]
                except UnicodeDecodeError:
                    pass  # Ignore decoding errors and continue reading the stream.
        except Exception as e:
            # Log unexpected errors. This could be any exception raised by
            # the reading or writing operations. Consider appending an error message
            # to `mem_buffer` to indicate that an error occurred.
            mem_buffer += "\n[Error reading stream: {}]".format(e)
        finally:
            # Ensure that the method always returns the buffer, even if an error occurred.
            return mem_buffer

    async def _process_poller(self, process: asyncio.subprocess.Process) -> int:
        keep_polling = True
        while keep_polling:
            time_till_next_heartbeat = self._task_instance_heartbeat_interval - (
                time() - self.last_heartbeat_time
            )
            try:
                await asyncio.wait_for(process.wait(), timeout=time_till_next_heartbeat)
                keep_polling = False
            except asyncio.TimeoutError:
                self.log_report_by()

        # keep typecheck happy
        returncode = process.returncode
        if returncode is None:
            raise AttributeError(
                "process finished polling but does not a a return code."
            )

        return returncode

    async def _run_cmd(self) -> None:
        # Copy the current environment variables and update them with additional settings
        env = os.environ.copy()
        env.update(self.command_add_env)

        # capture stdout and stderr for asynchronous reading
        process = await asyncio.create_subprocess_shell(
            self.command,
            env=env,
            stdout=asyncio.subprocess.PIPE,  # Captures stdout
            stderr=asyncio.subprocess.PIPE,  # Captures stderr
        )

        # Assert that stdout and stderr are not None for the type checker.
        assert process.stdout is not None
        assert process.stderr is not None

        # Initialize task variables to None. These will hold the asyncio tasks for
        # communicating with and monitoring the subprocess.
        stdout_task = stderr_task = heartbeat_task = None

        try:
            # Context manager to ensure file streams are properly closed after writing.
            with open(self.stdout, "w") as stdout_stream, open(
                self.stderr, "w"
            ) as stderr_stream:
                # Create asyncio tasks for reading subprocess stdout and stderr.
                stdout_task = asyncio.create_task(
                    self._communicate(process.stdout, stdout_stream)
                )
                stderr_task = asyncio.create_task(
                    self._communicate(process.stderr, stderr_stream)
                )
                # Task for monitoring the subprocess (e.g., for timeouts or heartbeats).
                heartbeat_task = asyncio.create_task(self._process_poller(process))

                # Await the completion of communication and monitoring tasks.
                # We gather all tasks together, ensuring they are completed before proceeding.
                valid_tasks = [stdout_task, stderr_task, heartbeat_task]
                await asyncio.gather(*valid_tasks)

        except Exception as e:
            # If an exception occurs, cancel all ongoing tasks to prevent dangling operations.
            tasks_to_cancel = [
                t for t in [stdout_task, stderr_task, heartbeat_task] if t is not None
            ]
            for task in tasks_to_cancel:
                task.cancel()
            # Await cancellation, ignoring any exceptions raised from cancellation.
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

            # Attempt a graceful shutdown of the subprocess if it's still running.
            process.send_signal(signal.SIGINT)
            try:
                # Wait for the process to terminate, with a specified timeout.
                await asyncio.wait_for(
                    process.wait(), timeout=self._command_interrupt_timeout
                )
            except asyncio.TimeoutError:
                # Forcefully terminate the subprocess
                process.kill()
                await process.wait()

            raise RuntimeError(
                f"Failed to execute command '{self.command}': {e}"
            ) from e

        finally:
            # After tasks have been handled and the subprocess is ensured to be terminated,
            # retrieve the results from the tasks if they were successfully completed.
            stdout_result = stderr_result = ""
            if stdout_task and stdout_task.done():
                stdout_result = stdout_task.result()
            if stderr_task and stderr_task.done():
                stderr_result = stderr_task.result()

            # Ensure the subprocess is fully terminated before exiting this method.
            returncode = await process.wait()

            # Update the task instance with the final results of command execution.
            self.set_command_output(
                returncode=returncode,
                stdout=stdout_result,
                stderr=stderr_result,
            )
