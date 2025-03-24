

def get_color_by_logtype(logtype: str) -> str:
    logtype = logtype.lower()

    match logtype:
        case 'info':
            return 'green'
        case 'warning':
            return 'yellow'
        case 'error':
            return 'red'
        case 'critical':
            return 'bold red'
        case 'debug':
            return 'blue'
        case _:
            return 'cyan'
