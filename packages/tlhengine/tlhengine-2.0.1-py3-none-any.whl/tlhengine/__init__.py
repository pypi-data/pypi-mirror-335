from . import dataset
from . import utils
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app.txt'),  # Log to a file
                        logging.StreamHandler()  # Also log to console
                    ])
# _logger = logging.getLogger(__name__)
# _logger.setLevel(logging.INFO)

# _console = logging.StreamHandler()
# _console.setLevel(logging.INFO)

# formatter = logging.Formatter("%(filename)s says %(levelname)s: %(message)s")
# _console.setFormatter(formatter)
# _logger.addHandler(_console)

# _logger.info("Initializing engine")
# for handler in _logger.handlers:
#     print(handler.__class__.__name__, ': from ', __file__ )