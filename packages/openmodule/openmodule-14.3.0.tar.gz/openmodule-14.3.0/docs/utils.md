# Utils

[TOC]

Here you can find some documentation of the other features of the Openmodule library.

## Presence

Helper class for listening to presence messages.

```python
from openmodule.utils.presence import PresenceListener

presence_listener = PresenceListener(core.messages)
presence_listener.on_enter.append(some_function)
```

## Signals

Helper class for listening on signals. 
```python
from openmodule.utils.signal_listener import SignalListener, FilterType

signal_listener = SignalListener(core.messages, core.rpc_client)
# register a listener for a signal with a filter_type specifying when the function should be called and optional tag
signal_listener.add_listener("gate1-open", FilterType.any_edge, some_function, tag="tag1")
signal_listener.add_listener("gate2-present_decision", FilterType.any_change, some_function2, tag="tag2")
# get the current value (and additional_data) of a signal, if unknown then RPC is called to get value
value = signal_listener.get_value("gate1-open")  
value, additional_data = signal_listener.get_value_and_additional_data("gate1-open")  
# trigger resending of signals via trigger_signals RPC for registered signals with specific tag 
# or all registered signals if tag is None
signal_listener.trigger_signals(tag="tag1")
# remove listeners with specific tag or all if tag is None
signal_listener.remove_listener(tag="tag1")
```


## Databox Upload

In the openmodule we have a utils function to simplify the upload with the databox service. The prerequisite is, 
that the upload folder `/data/om_service_databox_1/upload` is mounted correctly in the compose file to the `settings.DATABOX_UPLOAD_DIR` (default: `/upload`)

```python
from openmodule.utils.databox import upload

upload("/tmp/asdf.txt", "/enforcement/test/asdf.txt")
upload("/tmp/bsdf.csv", "exports/")  # same as exports/bsdf.csv as filename is taken from source if dst ends with /
```

docker-compose.yml example snippet
```yaml
    volumes:
    - /data/om_service_databox_1/upload/:/upload/
```

## Scheduling of Jobs

See [here](https://github.com/ts-accessio/schedule/tree/dateutil-support)

**⚠ Attention:** Do not import `schedule` yourself, openmodule imports 
the schedule version with dateutil support for you. 

## Documentation

Openmodule >= 3.0.5 features automatic generation of RPC and Message Schemas including their models. The generation uses
data that is generated during the test runs to create an OpenApi Schema. Your RPCs and Message handlers are
automatically documented if:

* You use the message dispatcher of the core (`OpenModuleCoreTestMixin`)
* You use the RPCServer of Openmodule

You can also register models yourself if you want them documented, but you may need to save the Schema in this case:

```python
from openmodule.utils.schema import Schema

Schema.save_model(Model)
Schema.save_rpc(channel, type, request, reqponse, handler)
Schema.save_message(topic, message_class, handler, filter)

Schema.to_file()
```

With default parameters, you need to document your handler functions with a doc string, that is then included as a
description.

