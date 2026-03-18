import time
import functools

def retry_with_backoff(max_retries=3, base_delay=2):
    """Decorator: retry a function with exponential backoff on failure."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    wait = base_delay ** attempt
                    print(f"[Retry] {func.__name__} failed (attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait}s...")
                    time.sleep(wait)
            raise RuntimeError(
                f"{func.__name__} failed after {max_retries} attempts. Last error: {last_error}"
            )
        return wrapper
    return decorator
