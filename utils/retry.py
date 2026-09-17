import time
from functools import wraps


def retry(
    max_attempts: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0
):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            current_delay = delay

            for attempt in range(
                1,
                max_attempts + 1
            ):

                try:

                    return func(
                        *args,
                        **kwargs
                    )

                except Exception as e:

                    print(
                        f"\n⚠️ {func.__name__} "
                        f"failed "
                        f"(attempt "
                        f"{attempt}/"
                        f"{max_attempts})"
                    )

                    print(
                        f"ERROR TYPE: {type(e).__name__}"
                    )

                    print(
                        f"ERROR: {e}"
                    )

                    if attempt == max_attempts:

                        print(
                            "\n❌ FINAL ERROR"
                        )

                        raise

                    print(
                        f"⏳ Retrying in "
                        f"{current_delay}s..."
                    )

                    time.sleep(
                        current_delay
                    )

                    current_delay *= backoff

        return wrapper

    return decorator