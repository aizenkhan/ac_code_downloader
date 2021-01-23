import logging

from app.logger import INFO_FORMATTER

# create the logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# defines the stream handler
_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_handler.setFormatter(logging.Formatter(INFO_FORMATTER))

# add the handler
log.addHandler(_handler)