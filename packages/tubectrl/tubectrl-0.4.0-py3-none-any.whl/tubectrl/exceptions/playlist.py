class PlaylistException(Exception):
    """Base exception for playlist exceptions."""


class ChannelClosedException(PlaylistException):
    """Exception raised when a channel is closed."""


class ChannelSuspendedException(PlaylistException):
    """Exception raised when a channel is suspended."""


class PlaylistForbiddenException(PlaylistException):
    """Exception raised when a playlist is forbidden."""


class ChannelNotFoundException(PlaylistException):
    """Exception raised when a channel is not found."""


class PlaylistNotFoundException(PlaylistException):
    """Exception raised when a playlist is not found."""


class PlaylistOperationUnsupportedException(PlaylistException):
    """Exception raised when a playlist operation is unsupported."""
