"""Setup logging for the project.

Assumed to be called before any other module is imported. Make sure no internal
modules are called from this file.

Note: In python, module content is loaded only once. Therefore we can safely
put the logic in the global scope.
"""

import logging

# Set logging level to ERROR for labelformat.
logging.getLogger("labelformat").setLevel(logging.ERROR)
