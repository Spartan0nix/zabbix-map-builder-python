import logging

logger = logging.getLogger('map-builder-logger')
logger.setLevel("DEBUG")
console_handler = logging.StreamHandler()
formatter = logging.Formatter('[map-builder][%(levelname)s] : %(message)s')

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
