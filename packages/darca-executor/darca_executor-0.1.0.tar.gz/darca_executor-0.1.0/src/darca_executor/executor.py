import subprocess  # nosec B404 - subprocess is explicitly controlled
from typing import List, Optional, Union

from darca_exception.exception import DarcaException
from darca_log_facility.logger import DarcaLogger  # Adjust import if needed

logger = DarcaLogger(name="executor", level="DEBUG").get_logger()


class DarcaExecError(DarcaException):
    """Custom exception to wrap subprocess errors consistently."""

    def __init__(
        self,
        message: str,
        *,
        command=None,
        returncode=None,
        stdout=None,
        stderr=None,
        cause=None
    ):
        metadata = {
            "command": command,
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
        }
        super().__init__(
            message,
            error_code="DARCA_EXEC_ERROR",  # ✅ Explicit error code
            metadata=metadata,
            cause=cause,
        )


class DarcaExecutor:
    """
    Secure subprocess wrapper for executing shell and non-shell commands.

    Usage:
        executor = DarcaExecutor(use_shell=False)
        result = executor.run(["echo", "hello world"])
    """

    def __init__(self, use_shell: bool = False):
        """
        Initialize executor.

        Args:
            use_shell (bool): If True, executes commands through the shell.
        """
        self.use_shell = use_shell

    def run(
        self,
        command: Union[List[str], str],
        capture_output: bool = True,
        check: bool = True,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
        timeout: Optional[int] = 30,
    ) -> subprocess.CompletedProcess:
        """
        Execute a command with subprocess.run and return the result.

        Args:
            command (List[str] | str): Command to run.
            capture_output (bool): If True, captures stdout/stderr.
            check (bool): Raise CalledProcessError on non-zero exit.
            cwd (Optional[str]): Run command from this directory.
            env (Optional[dict]): Environment variables.
            timeout (Optional[int]): Timeout in seconds.

        Returns:
            subprocess.CompletedProcess: Completed process result.

        Raises:
            ValueError: If command type does not match shell usage.
            DarcaExecError: On subprocess failure with context.
        """
        if self.use_shell:
            if not isinstance(command, str):
                raise ValueError(
                    "When use_shell=True, command must be a string."
                )
        else:
            if not isinstance(command, list):
                raise ValueError(
                    "When use_shell=False, command must be a list of args."
                )

        logger.debug("Running command: %s", command)
        logger.debug("Shell mode: %s", self.use_shell)
        logger.debug("Working directory: %s", cwd)
        logger.debug("Capture output: %s", capture_output)
        logger.debug("Environment: %s", env)
        logger.debug("Timeout: %s seconds", timeout)

        try:
            result = subprocess.run(  # nosec B602
                command,
                capture_output=capture_output,
                check=check,
                cwd=cwd,
                env=env,
                timeout=timeout,
                text=True,
                shell=self.use_shell,
            )
            logger.debug(
                "Command completed with return code %d", result.returncode
            )
            if capture_output:
                logger.debug("STDOUT: %s", result.stdout.strip())
                logger.debug("STDERR: %s", result.stderr.strip())
            return result

        except subprocess.CalledProcessError as e:
            logger.error("Command failed with return code %d", e.returncode)
            logger.error("STDOUT: %s", e.stdout)
            logger.error("STDERR: %s", e.stderr)
            raise DarcaExecError(
                "Command failed with non-zero exit code.",
                command=e.cmd,
                returncode=e.returncode,
                stdout=e.stdout,
                stderr=e.stderr,
                cause=e,
            )

        except subprocess.TimeoutExpired as e:
            logger.error("Command timed out after %s seconds", timeout)
            raise DarcaExecError(
                "Command timed out.",
                command=e.cmd,
                returncode=None,
                stdout=e.output,
                stderr=e.stderr,
                cause=e,
            )

        except subprocess.SubprocessError as e:
            logger.exception("Unexpected subprocess error occurred.")
            raise DarcaExecError(
                "Subprocess error occurred.",
                command=command,
                returncode=None,
                cause=e,
            )

        except Exception as e:
            logger.exception(
                "Unexpected error occurred during subprocess execution."
            )
            raise DarcaExecError(
                "Unexpected error during command execution.",
                command=command,
                returncode=None,
                cause=e,
            )
