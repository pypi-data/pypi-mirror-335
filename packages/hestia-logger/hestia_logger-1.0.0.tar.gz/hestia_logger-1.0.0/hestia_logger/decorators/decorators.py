import functools
import time
import asyncio
import json
import inspect
import traceback
import os
from hestia_logger.core.custom_logger import get_logger

SENSITIVE_KEYS = {"password", "token", "secret", "apikey", "api_key", "credential"}


def mask_sensitive_data(kwargs):
    return {
        key: "***" if key.lower() in SENSITIVE_KEYS else value
        for key, value in kwargs.items()
    }


def safe_serialize(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except TypeError:
        return str(obj)


def get_caller_script_name():
    """Returns the filename of the script that called the decorated function,
    while handling pytest execution correctly."""
    stack = inspect.stack()

    for frame in reversed(stack):  # Traverse the call stack from the outermost call
        script_path = frame.filename
        if "pytest" not in script_path:  # Ignore pytest internals
            script_name = os.path.basename(script_path).replace(".py", "")
            return script_name

    return "unknown_script"


def log_execution(func=None, *, logger_name=None):
    if func is None:
        return lambda f: log_execution(f, logger_name=logger_name)

    # Use the actual script filename instead of "__main__"
    caller_script_name = get_caller_script_name()
    service_logger = get_logger(logger_name or caller_script_name)
    app_logger = get_logger("app", internal=True)

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_kwargs = mask_sensitive_data(kwargs)

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
                "service": service_logger.name,
                "function": func.__name__,
                "status": "started",
                "args": safe_serialize(args),
                "kwargs": safe_serialize(sanitized_kwargs),
            }

            app_logger.info(json.dumps(log_entry, ensure_ascii=False))
            service_logger.info(f"📌 Started: {func.__name__}()")

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        "result": safe_serialize(result),
                    }
                )

                app_logger.info(json.dumps(log_entry, ensure_ascii=False))
                service_logger.info(
                    f"✅ Finished: {func.__name__}() in {duration:.4f} sec"
                )

                return result
            except Exception as e:
                log_entry.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )

                app_logger.error(json.dumps(log_entry, ensure_ascii=False))
                service_logger.error(f"❌ Error in {func.__name__}: {e}")

                raise

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_kwargs = mask_sensitive_data(kwargs)

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
                "service": service_logger.name,
                "function": func.__name__,
                "status": "started",
                "args": safe_serialize(args),
                "kwargs": safe_serialize(sanitized_kwargs),
            }

            app_logger.info(json.dumps(log_entry, ensure_ascii=False))
            service_logger.info(f"📌 Started: {func.__name__}()")

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        "result": safe_serialize(result),
                    }
                )

                app_logger.info(json.dumps(log_entry, ensure_ascii=False))
                service_logger.info(
                    f"✅ Finished: {func.__name__}() in {duration:.4f} sec"
                )

                return result
            except Exception as e:
                log_entry.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )

                app_logger.error(json.dumps(log_entry, ensure_ascii=False))
                service_logger.error(f"❌ Error in {func.__name__}: {e}")

                raise

        return sync_wrapper
