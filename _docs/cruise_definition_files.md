---
permalink: /cruise_definition_files/
title: "Cruise Definition Files"
layout: single
toc: true
toc_label: "Contents"
toc_icon: "list"
toc_sticky: true  # Makes the TOC stick on scroll
---

## Overview

Please see the [Introduction to OpenRVDAS Loggers]({{ "/intro_to_loggers/" | relative_url }}) and 
[Logger Configurations Files]({{ "/logger_configuration_files/" | relative_url }}) for a general introduction to loggers and their configuration files.

## Cruise Definitions

A typical cruise will involve many loggers running in parallel, typically one for each sensor. Additionally, each logger may need to run one of several different configurations depending on the phase of the cruise (such as "in port", "in EEZ" or "underway"). An OpenRVDAS _cruise definition file_ specifies all of these configurations, associates them with specific loggers, and allows creating "modes" such as `port`, `EEZ`, `underway`, etc, to support different phases of ship operation.

It is this cruise definition file that is loaded by the OpenRVDAS GUI, or by the Logger Manager when run from the command line.

At present there are two ways to specify a cruise definition file - the traditional "expanded" format, and a newer, compact "templatized" format. We describe both below:

### A Traditional Cruise Definition File

Like individual configurations, a full cruise definition file (such as
[NBP1406_cruise.yaml](https://github.com/OceanDataTools/openrvdas/blob/master/test/NBP1406/NBP1406_cruise.yaml)) will be specified in YAML as a dict. It will contain a dictionary of all its logger configurations under a `configs` key, mapping  configuration names to the configuration definitions themselves.
```
configs:
  gyr1->off:
    name: gyr1->off  # config name; no readers/writers etc. means it's off
  gyr1->net:
    name: gyr1->net  # config name
    readers:
      class: SerialReader
      kwargs:
        baudrate: 9600
        port: /dev/ttyr15
    transforms:
      ...
    writers:
      ...
  gyr1->file/net/db:
    name: gyr1->file/net/db  # config name
    ...
  ...
```

#### Loggers

The set of configs that are associated with a particular "logger" are listed under that logger's name under a top-level `loggers:` key:
```
loggers:
  eng1:
    configs:
    - eng1->off
    - eng1->net
    - eng1->file/net/db
  gyr1:
    configs:
    - gyr1->off
    - gyr1->net
    - gyr1->file/net/db
  knud:
    configs:
    - knud->off
    - knud->net
    - knud->file/net/db
  mwx1:
    configs:
    - mwx1->off
    - mwx1->net
    - mwx1->file/net/db
  rtmp:
    configs:
    - rtmp->off
    - rtmp->net
    - rtmp->file/net/db
  s330:
    configs:
    - s330->off
    - s330->net
    - s330->file/net/db
```


#### Modes

Typically, a vessel will have sets of logger configurations that
should all be run together: which should be running when in port, when
underway, etc.

To accommodate easy reference to these modes of operation, we include
a "mode" dictionary in our configuration file:. Each mode
definition is a dict the keys of which are logger names, and the
values are the names of the logger configurations that should be run
when that mode is selected. To illustrate:
```
# Which configs should be running when in which mode
modes:
  'off':
    eng1: eng1->off
    gyr1: gyr1->off
    knud: knud->off
    mwx1: mwx1->off
    rtmp: rtmp->off
    s330: s330->off
  port:
    eng1: eng1->net
    gyr1: gyr1->net
    knud: knud->off
    mwx1: mwx1->net
    rtmp: rtmp->off
    s330: s330->net
  underway:
    eng1: eng1->file/net/db
    gyr1: gyr1->file/net/db
    knud: knud->file/net/db
    mwx1: mwx1->file/net/db
    rtmp: rtmp->file/net/db
    s330: s330->file/net/db
default_mode: 'off  # In quotes because 'off' is a YAML keyword
```
For accounting purposes, our convention is to include an empty
configuration in the "configs" dict to denote the configuration of a
logger that isn't running.

Note also the additional (and optional) ```default_mode``` key
in the cruise configuration. It specifies that, lacking any other
information, which mode the system should be initialized to on startup.

#### Cruise Metadata

By convention, each cruise definition file should also include a `cruise:` key indicating the cruise name, its start and end dates, and any other metadata the operator feels relevant. At present, the only use that is made of this section is that the cruise id is displayed at the top of the OpenRVDAS web GUI.
```
# Optional cruise metadata
cruise:
  id: NBP1406
  start: "2014-06-01"  # Quoted so YAML doesn't auto-convert to a datetime
  end: "2014-07-01"
```
As indicated above, a sample full cruise definition file may be viewed at
[NBP1406_cruise.yaml](https://github.com/OceanDataTools/openrvdas/blob/master/test/NBP1406/NBP1406_cruise.yaml).


### Templated Cruise Definition Files

The traditional way of specifying a cruise definition file is...verbose. The sample `NBP1406_cruise` is over 1500 lines, and and difficult to maintain or modify. To date, different institutions have coped with this by generating these files mechanically, either from customized scripts or databases. We have recently implemented a templatized format for specifying cruise definitions that promises to drastically reduce this complexity. Templatized cruise definitions may be loaded the same way as traditional cruise definitions - OpenRVDAS will recognize and expand them internally.

#### Logger Templates

The crucial element of a templatized cruise definition is a logger template. Many loggers in a typical installation will be almost identical, varying only by a few fields, such as ports, or prefixes to be attached.

The [serial_logger_template](https://github.com/OceanDataTools/openrvdas/blob/master/local/logger_templates/serial_logger_template.yaml) encodes a typical set of logger configurations for a serial-port-based instrument:
```buildoutcfg
###################
logger_templates:

  #################
  serial_logger_template:
    configs:
      'off': {}
      
      # Read, timestamp, prefix, and send off to net via UDP
      net:
        readers:
        - class: SerialReader
          kwargs:
            baudrate: <<baud_rate>>
            port: <<serial_port>>
        transforms:
        - class: TimestampTransform
        - class: PrefixTransform
          kwargs:
            prefix: <<logger>>
        writers:
        - class: UDPWriter
          kwargs:
            port: <<raw_udp_port>>
            destination: <<udp_destination>>
            
      # Write both to network and save to file
      net+file:
        readers:
        - class: SerialReader
          kwargs:
            baudrate: <<baud_rate>>
            port: <<serial_port>>
        transforms:
        - class: TimestampTransform
        writers:
        - class: LogfileWriter
          kwargs:
            filebase: <<file_root>>/<<logger>>/raw/<<cruise>>_<<logger>>
        - class: ComposedWriter
          kwargs:
            transforms:
            - class: PrefixTransform
              kwargs:
                prefix: <<logger>>
            writers:
              - class: UDPWriter
                kwargs:
                  port: <<raw_udp_port>>
                  destination: <<udp_destination>>

```

Note the names enclosed in `<<double_brackets>>`; these will be filled in by variables on a logger-by-logger basis in the cruise definition file:

```buildoutcfg
###########################################################
# Global variables - can be overridden by individual loggers
variables:
  cruise: NBP1406
  raw_udp_port: 6224
  udp_destination: 255.255.255.255  
  file_root: /var/tmp/log
 
###########################################################
loggers:
  PCOD:
    logger_template: serial_logger_template
    variables:
      serial_port: /tmp/tty_PCOD
      baud_rate: 4800
  cwnc:
    logger_template: serial_logger_template
    variables:
      serial_port: /tmp/tty_cwnc
      baud_rate: 19200
```

No separate `configs` section is needed in this case - the loggers are fully specified by referencing the template.

The logger templates may either be included directly in the cruise definition file under the `logger_templates:` key, as above, or included by reference from an `includes:` section:
```buildoutcfg
###########################################################
includes:
  - local/logger_templates/serial_logger_template.yaml
  - local/logger_templates/parse_data_logger_template.yaml
  - local/logger_templates/true_winds_logger_template.yaml
  - local/logger_templates/snapshot_logger_template.yaml
```
Note that filepaths specified in the `includes` block may include wildcards such as `*`, and the files may themselves have an `includes` section. All logger templates are merged into the top-level dict, with later keys overwriting earlier ones.

Non-fully-specified paths will use the base installation directory (typically `/opt/openrvdas`), but this may be overridden by means of a top-level `includes_base_dir` key:

```buildoutcfg
###########################################################
includes_base_dir: /opt/local/logger_templates
includes:
  - *_logger_template.yaml
```

#### One-Off Inline Loggers

Loggers that are one-off, that is, specialized enough that there is no advantage to creating a template for them, may be included inline. That is, the configs for the logger may be defined when the logger is:

```buildoutcfg
loggers:
  # Templatized logger
  PCOD:
    logger_template: serial_logger_template
    variables:
      serial_port: /tmp/tty_PCOD
      baud_rate: 4800

  # One-off, inline logger for geofencing
  geo_fencing:
    configs:
      off: {}
      on:
      readers: {class: UDPReader, kwargs: {port: 7221}}
      transforms:
        - class: ParseTransform
      ....
```

#### Mixing and Matching - under the hood

As illustrated above, these approaches can be mixed and matched in the same cruise definition. In fact, while it's not recommended for clarity's sake, templatized and inline logger definitions can also be mixed with the traditional logger style of definition. This is because internally, before passing them on to the Logger Manager, the system begins by looking for logger templates and expands them into inline definitions. It then propagates the inline definitions into the separate top leve `configs` key. Loggers that already have inline definitions or configurations defined in the top-level `configs` key will be unaffected, unless overwritten by conflicting templatized loggers. 

#### Modes

The `modes` section - at present - remains unchanged and relatively verbose, with one important difference. If no `modes` key is found, the system will try to infer one. It will create a single default mode such that every logger is running the first configuration defined for it (in the case of `serial_logger_template`, this would be `off`).

This simplication allows institutions who have only one operating mode (and rely on the system to simply 'come up logging') to define loggers with only one configuration and simply omit creating a 'modes' section.

If there _are_ other configurations, they will still be accessible via the GUI or command line interface. The only difference is that they will be have to activated on a per-logger basis, rather than all at once using cruise mode selection.
