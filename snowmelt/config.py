# Import our base configuration.
from snowmelt.config_base import *

# Try to import any local configuration.
try:
    from snowmelt.config_local import *
except ImportError:
    print 'Warning: No config_local.py file found, using config_base'
