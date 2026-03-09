from slowapi import Limiter
from slowapi.util import get_remote_address

# this is the rate limiter for authors, auth and users
limiter = Limiter(key_func=get_remote_address, application_limits=['20/minute'])
