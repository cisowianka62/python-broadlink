"""Exceptions for Broadlink devices."""
import collections
import struct


class BroadlinkException(Exception):
    """Base class common to all Broadlink exceptions."""

    def __init__(self, *args, **kwargs):
        """Initialize the exception."""
        super().__init__(*args, **kwargs)
        if len(args) >= 2:
            self.errno = args[0]
            self.strerror = ": ".join(str(arg) for arg in args[1:])
        elif len(args) == 1:
            self.errno = None
            self.strerror = str(args[0])
        else:
            self.errno = None
            self.strerror = ""

    def __str__(self):
        """Return str(self)."""
        if self.errno is not None:
            return "[Errno %s] %s" % (self.errno, self.strerror)
        return self.strerror

    def __eq__(self, other):
        """Return self==value."""
        # pylint: disable=unidiomatic-typecheck
        return type(self) == type(other) and self.args == other.args

    def __hash__(self):
        """Return hash(self)."""
        return hash((type(self), self.args))


class MultipleErrors(BroadlinkException):
    """Multiple errors."""

    def __init__(self, *args, **kwargs):
        """Initialize the exception."""
        errors = args[0][:] if args else []
        counter = collections.Counter(errors)
        strerror = "Multiple errors occurred: %s" % counter
        super().__init__(strerror, **kwargs)
        self.errors = errors

    def __repr__(self):
        """Return repr(self)."""
        return "MultipleErrors(%r)" % self.errors

    def __str__(self):
        """Return str(self)."""
        return self.strerror


class AuthenticationError(BroadlinkException):
    """Authentication error."""


class AuthorizationError(BroadlinkException):
    """Authorization error."""


class CommandNotSupportedError(BroadlinkException):
    """Command not supported error."""


class ConnectionClosedError(BroadlinkException):
    """Connection closed error."""


class StructureAbnormalError(BroadlinkException):
    """Structure abnormal error."""


class DeviceOfflineError(BroadlinkException):
    """Device offline error."""


class ReadError(BroadlinkException):
    """Read error."""


class SendError(BroadlinkException):
    """Send error."""


class SSIDNotFoundError(BroadlinkException):
    """SSID not found error."""


class StorageError(BroadlinkException):
    """Storage error."""


class WriteError(BroadlinkException):
    """Write error."""


class NetworkTimeoutError(BroadlinkException):
    """Network timeout error."""


class DataValidationError(BroadlinkException):
    """Data validation error."""


class UnknownError(BroadlinkException):
    """Unknown error."""


BROADLINK_EXCEPTIONS = {
    # Firmware-related errors are generated by the device.
    -1: (AuthenticationError, "Authentication failed"),
    -2: (ConnectionClosedError, "You have been logged out"),
    -3: (DeviceOfflineError, "The device is offline"),
    -4: (CommandNotSupportedError, "Command not supported"),
    -5: (StorageError, "The device storage is full"),
    -6: (StructureAbnormalError, "Structure is abnormal"),
    -7: (AuthorizationError, "Control key is expired"),
    -8: (SendError, "Send error"),
    -9: (WriteError, "Write error"),
    -10: (ReadError, "Read error"),
    -11: (SSIDNotFoundError, "SSID could not be found in AP configuration"),
    # SDK related errors are generated by this module.
    -2040: (DataValidationError, "Device information is not intact"),
    -4000: (NetworkTimeoutError, "Network timeout"),
    -4007: (DataValidationError, "Received data packet length error"),
    -4008: (DataValidationError, "Received data packet check error"),
    -4009: (DataValidationError, "Received data packet information type error"),
    -4010: (DataValidationError, "Received encrypted data packet length error"),
    -4011: (DataValidationError, "Received encrypted data packet check error"),
    -4012: (AuthorizationError, "Device control ID error"),
}


def exception(err_code: int) -> BroadlinkException:
    """Return exception corresponding to an error code."""
    try:
        exc, msg = BROADLINK_EXCEPTIONS[err_code]
        return exc(err_code, msg)
    except KeyError:
        return UnknownError(err_code, "Unknown error")


def check_error(error: bytes) -> None:
    """Raise exception if an error occurred."""
    error_code = struct.unpack("h", error)[0]
    if error_code:
        raise exception(error_code)