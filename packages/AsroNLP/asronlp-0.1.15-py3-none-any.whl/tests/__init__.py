# __init__.py in tests directory
import logging

# Configure logging at the package level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Now all modules in this package can use logging
