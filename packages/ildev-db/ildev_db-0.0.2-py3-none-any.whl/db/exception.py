from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import logging

logger = logging.getLogger(__name__)

class BaseRepositoryError(Exception):
    """Custom exception for base repository errors."""
    pass

def handle_db_exceptions(allow_return=False, return_data=None):
    def decorator(func): 
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self = args[0] 
            current_method_name = func.__name__
            model_name = self.model.__name__ if hasattr(self, "model") else "UnknownModel"

            try:
                return await func(*args, **kwargs)
            except IntegrityError as e:
                error_text = f"Duplicate entry detected in {current_method_name}() for {model_name}: {e}"
            except NoResultFound as e:
                error_text = f"No result found in {current_method_name}() for {model_name}: {e}"
            except SQLAlchemyError as e:
                error_text = f"Database error in {current_method_name}() for {model_name}: {e}"
            except Exception as e:
                error_text = f"Unexpected error in {current_method_name}() for {model_name}: {e}"                
            finally:
                if "error_text" in locals():
                    logger.error(error_text)
                    if allow_return:
                        return return_data
                    else:
                        raise BaseRepositoryError(error_text)
        return wrapper
    return decorator