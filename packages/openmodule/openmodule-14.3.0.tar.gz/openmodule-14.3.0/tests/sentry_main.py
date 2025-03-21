import os
import sys
import time

import sentry_sdk

from openmodule import sentry


class SlowSentryTransport(sentry_sdk.HttpTransport):
    def _send_envelope(self, envelope):
        time.sleep(1)
        with open("/tmp/flush_test", "ab") as f:
            f.write(b"---\n")


def main():
    exit_func = None
    if len(sys.argv) > 1:
        exit_func = sys.argv[1]
        if exit_func == "os":
            exit_func = os._exit
        elif exit_func == "sys":
            exit_func = sys.exit
    sentry.init_sentry(dsn="http://test@test/1", transport=SlowSentryTransport)
    sentry_sdk.capture_message("test")
    if exit_func:
        exit_func(0)


if __name__ == '__main__':
    main()
