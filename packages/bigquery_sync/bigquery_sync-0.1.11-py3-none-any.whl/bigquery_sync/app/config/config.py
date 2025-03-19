RETRY_COUNT = 3

SCHEDULED_QUERIES = '_scheduled_queries'


DEFAULT_SCHEDULED_CONFIG_JSON = {
    "configuration": {
        "schedule": {
            "repeat": {
                "hourly": 24,
                "weekly": None,
                "monthly": None
            },
            "time": {
                "hour": 0,
                "minute": 30
            }
        },
        "destination": {
            "dataset": "",
            "table": None
        },
        "write_mode": None
    }
}
