---
permalink: /guide/your-vessel/
title: "Setting Up Your Own Vessel"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
This section turns a fresh installation into *your ship's* system, in the
order you'd actually do the work: set up your institution's repository,
write a cruise definition, build and test loggers for your instruments,
and teach the system to parse what they say. It ends with a worked
example that does all of it for one new sensor.

# Your Institution's Repository and local/

*Not yet rewritten. In the meantime, see
[Your Institution's Code and Configuration]({{ "/local_code/" | relative_url }}).*

Keeping your vessel's definitions, device types and custom code in your
own repository, linked into `local/` — so OpenRVDAS upgrades never touch
your configuration and your configuration is under your version control.

# Writing a Cruise Definition

*Not yet rewritten. In the meantime, see
[Cruise Definition Files]({{ "/cruise_definition_files/" | relative_url }})
and [Logger Configuration Files]({{ "/logger_configuration_files/" | relative_url }}),
with [A Short Introduction to YAML]({{ "/yaml/" | relative_url }}) if YAML
is new to you.*

The `loggers`, `configs` and `modes` sections; config templates; includes;
and validating the result with `validate_config`.

# Creating and Testing Loggers

*Not yet rewritten. In the meantime, see
[Introduction to Loggers]({{ "/intro_to_loggers/" | relative_url }}) and
[The Listener Script]({{ "/listen_py/" | relative_url }}).*

Building a logger configuration a stage at a time with `listen`, testing
it against simulated data, then dropping it into the cruise definition.

# Readers for Your Hardware

*Not yet rewritten. In the meantime, see
[Reading from Serial Ports]({{ "/serial_readers/" | relative_url }}) and
[Reading from Modbus Devices]({{ "/modbus_readers/" | relative_url }}).*

Serial ports (and their permissions), UDP and TCP sources, MQTT and
modbus — and writing a custom Reader when nothing on the shelf speaks
your instrument's protocol.

# Parsing and Device Types

*Not yet rewritten. In the meantime, see
[Record Parsing]({{ "/parsing/" | relative_url }}) and the
[NMEA Device Type Library]({{ "/nmea_device_types/" | relative_url }}).*

How parsed fields get their names: device and device type definitions,
the bundled NMEA library, writing definitions for your own instruments,
and checking them with `check_parse_format`.

# Worked Example: Adding a Sensor

*Not yet rewritten. In the meantime, see
[Adding a Sensor]({{ "/adding_a_sensor/" | relative_url }}).*

A new instrument, end to end: reader, device type, logger configurations,
cruise definition entries, and a display — using everything above.
