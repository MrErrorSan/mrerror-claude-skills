from .reports import daily

REPORTS = {"daily": daily.run}


def get(name: str):
    return REPORTS[name]
