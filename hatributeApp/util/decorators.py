import json
import traceback
from flask import request, g

from hatributeApp import app
from hatributeApp.DB.db_auth import handel_session_request


# Decorator : Checks if request is json and then checks if the session is correct. If all of these are true call decorated function
def only_with_session(func):
    def decorator():
        if request.is_json:
            try:
                data = request.get_json()
                handel_session_request(data)
                if g.user:
                    return_data, error_code = func(data)
                else:
                    return_data, error_code = json.dumps(g.data), 400
                return str(return_data), error_code
            except:
                app.logger.error(f"{func.__name__} : " + traceback.format_exc())
                return "Internal server error", 500
        else:
            return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406

    # Renaming the decorator name so that flask doesnt get confused
    decorator.__name__ = func.__name__
    return decorator


# Decorator : Checks if request is json and if yes, parse it and pass it to the decorated function
def only_json_request(func):
    def decorator():
        try:
            if request.is_json:
                data = request.get_json()
                return_data, error_code = func(data)
                return str(return_data), error_code
            else:
                return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406
        except:
            app.logger.error(f"{func.__name__} : " + traceback.format_exc())
            return "Internal server error", 500

    # Renaming the decorator name so that flask doesnt get confused
    decorator.__name__ = func.__name__
    return decorator