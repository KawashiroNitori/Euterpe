class NotFoundError(Exception):
    pass


class SongNotFoundError(NotFoundError):
    pass


class SongCannotDownloadError(NotFoundError):
    pass
