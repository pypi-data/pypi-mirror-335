#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""\
exceptions provides the class PySlkException, which is the general
exception for the pyslk package.
"""

__all__ = [
    "ArchiveError",
    "check_for_errors",
    "HostNotReachableError",
    "PySlkException",
    "PySlkNoValidLoginTokenError",
    "PySlkNothingToRecallError",
    "PySlkBadFileError",
    "PySlkBadProcessError",
    "PySlkEmptyInputError",
    "SizeMismatchError",
    "SlkIOError",
]


class PySlkException(Exception):
    """A PySlkException derived from 'Exception'"""

    pass


class PySlkNoValidLoginTokenError(PySlkException):
    pass


class PySlkBadFileError(PySlkException):
    pass


class PySlkNothingToRecallError(PySlkException):
    pass


class PySlkBadProcessError(PySlkException):
    pass


class ArchiveError(PySlkException):
    stdout = ["Archive failed"]
    pass


class PySlkEmptyInputError(PySlkException):
    pass


class SlkIOError(PySlkException):
    stdout = ["Unable to create namespace", "Namespace not found in list command"]
    pass


class HostNotReachableError(ArchiveError):
    stdout = ["Host not reachable"]
    pass


class SizeMismatchError(ArchiveError):
    pass


def check_for_errors(output, fun):
    """Check subprocess output for certain errors"""
    if output.returncode != 0:
        stdout = output.stdout.decode("utf-8")
        stderr = output.stderr.decode("utf-8")
        error = (
            f"pyslk.{fun}\n"
            f"args: {output.args}\n"
            f"command: {' '.join(output.args)}\n"
            f"errorcode: {output.returncode}\n"
            f"stdout: {stdout}"
            f"stderr: {stderr}"
        )

        if any([io in stdout for io in HostNotReachableError.stdout]):
            raise HostNotReachableError(error)

        if any([io in stdout for io in SlkIOError.stdout]):
            raise SlkIOError(error)

        if any([io in stdout for io in ArchiveError.stdout]):
            raise ArchiveError(error)

        # This returncode is different from the output in ~/.slk/slk-cli.log
        # we cannot distinguish archive errors by their error code yet.
        # if output.returncode == 400:
        #    raise SizeMismatchError(error)

        raise PySlkException(error)

    return output.returncode
