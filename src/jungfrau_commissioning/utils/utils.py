from datetime import datetime


class text_colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELL = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def date_time_string():
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
