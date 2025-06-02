# Import and re-export contact-related modules for backward compatibility
from adapter.contacts.directory_api import *
from adapter.contacts.fallback import *
from adapter.contacts.resolution import *

# Import and re-export calendar-related modules for backward compatibility
from adapter.calendar.auth import *
from adapter.calendar.events import *
from adapter.calendar.queries import *

# Import and re-export weather-related modules for backward compatibility
from adapter.weather.client import *
from adapter.weather.alerts import *
from adapter.weather.forecast import *

# Import and re-export common modules
from adapter.common.auth import *
