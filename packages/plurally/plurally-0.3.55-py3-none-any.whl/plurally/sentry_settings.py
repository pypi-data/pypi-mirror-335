import os

import sentry_sdk

sentry_dsn = os.environ.get("SENTRY_URL")

if sentry_dsn:
    print("Sentry URL found, initializing Sentry")
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=0,
    )
