import arrow


def datetime_now() -> str:
    now = arrow.now().format("YYYY-MM-DD HH:mm:ss")
    return now


def datetime_delta(start_datetime_str: str, end_datetime_str: str) -> int:
    start_datetime = arrow.get(start_datetime_str).datetime
    end_datetime = arrow.get(end_datetime_str).datetime
    total_seconds = (end_datetime - start_datetime).total_seconds()
    delta = int(total_seconds)
    return delta
