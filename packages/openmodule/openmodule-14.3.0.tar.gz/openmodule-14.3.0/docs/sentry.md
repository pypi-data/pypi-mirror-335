from openmodule.core import init_openmodule

# Sentry

[TOC]

## Introduction

Sentry is a service that helps us monitor and fix errors in our applications. It provides real-time error tracking and
notifications.

The Python Sentry SDK automatically creates events from uncaught exceptions and logs of level `error` and above.
All error logs and exceptions are part of a transaction, even if no trace is created. So adding additional context to a
transaction will also apply to the error logs and exceptions.

It also provides tools for tracing process flows and diagnosing performance issues.

## Initialization

To use Sentry, you need to provide the DSN to the OpenModuleCore initialization function. The DSN is a unique identifier
for your project that tells the SDK where to send the events. You can find the DSN in the Sentry project settings.

* During Testing and Development, sentry will not be initialized, and no events will be sent.
* You can provide additional [sentry options](https://docs.sentry.io/platforms/python/configuration/options/) as keyword
  arguments to the `init_openmodule` function (`server_name` and `environment` cannot be overriden).
* the `extras` keyword argument can be used to provide additional data to the Sentry SDK
* the `topics_to_ignore` keyword argument can be used to provide a list of topics that should not be captured by Sentry.
You should also check that no trace will be started for every message from that topic. (defaults to `["io"]`)
* the `functions_to_ignore` keyword argument can be used to provide a list of span names (auto generated for functions)
that should not be captured by Sentry. (defaults to `[]`)

```python
def main():
    core = init_openmodule(settings, dsn="https://<key>@debug.acc.si/<project>")
```

## Errors & Exceptions

Uncaught exceptions and `logging.exception(...)` calls are automatically captured by Sentry and turned into issues with
a stack trace. `logging.error(...)` calls are also captured, but without a stack trace, so it's better to use
`logging.exception(...)` when possible.

### requests raise_for_status

When using the `requests` library, you can use the `raise_for_status` method to raise an exception if the request was
unsuccessful. This will cause sentry to automatically add the response body to the current transaction.

## Tracing

Openmodule provides the `sentry.trace` function that can be used as a decorator to trace a function or as a context
manager to trace a block of code. This will create a new span for the function or block of code and record its duration.
If no transaction is active, a new transaction will be created before the span.

* When using the decorator, the span will have the (qual)name of the function (if none is provided).
* When using the context manager, you **should** provide a name for the span.
* In addition to name, the op parameter can be used to specify the operation type of the span.
  (default is `function` and should be sufficient for most cases, others can be found
  [here](https://develop.sentry.dev/sdk/telemetry/traces/span-operations/).)

```python
from openmodule import sentry


@sentry.trace
def my_function():
    pass


@sentry.trace(name="other_function")
def my_function2():
    pass


with sentry.trace("my_block"):
    pass
```

## Adding Additional Information

You can add context to the current transaction using one of the following methods:

* Adding the data as kwargs to the `sentry.trace` function.
  * `sentry.trace("my_block", extras={"key": "value"}, tags={"key": "value"}, context={"key": "value"})`
* `sentry_sdk.set_tag(key: str, value: str)`: Adds
  a [tag](https://docs.sentry.io/platforms/python/enriching-events/tags/) to the current transaction.
* `sentry_sdk.set_tags(**key_value_pairs: str)`:
  Adds [tags](https://docs.sentry.io/platforms/python/enriching-events/tags/) to the current transaction.
* `sentry_sdk.set_context(key: str, value: Any)`: Adds
  a [context](https://docs.sentry.io/platforms/python/enriching-events/context/) to the current transaction.
* `sentry_sdk.set_extra(key: str, value: Any)`: Adds extra data to the current transaction. (similar to tags, but not
  indexed for searching and more free-form)

```python
with sentry.trace("my_block"):
    sentry_sdk.set_tag("key", "value")
    sentry_sdk.set_tags({"key1": "value1", "key2": "value2"})
    sentry_sdk.set_context("key", {"whatever": "you want"})
    sentry_sdk.set_extra("key", "value")
```
