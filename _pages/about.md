---
permalink: /about/
title: "About"
---

The Open Research Vessel Data Acquisition System (OpenRVDAS) is a software framework used for building custom data acquisition systems (DAS). OpenRVDAS target audiences are oceanographic research vessel operators and operators of other science-related platforms that have the need to record streaming data. OpenRVDAS is capable of reading data records from serial ports and network-aware sensors, optionally modifying those data records and streaming either the result to one or more destinations, including logfiles, network ports, databases, etc.

OpenRVDAS is designed to be modular and extensible, relying on simple composition of Readers, Transforms and Writers to achieve the needed datalogging functionality.

The project code repository is at [https://github.com/oceandatatools/openrvdas](https://github.com/oceandatatools/openrvdas), and is made available under the [MIT Open Source License](https://opensource.org/license/mit).

## Where to start?
* [OpenRVDAS Quickstart](../_pages/quickstart.md) if you want to just grab the code and poke around with basic loggers as quickly as possible.
* [GUI Quickstart](../_pages/quickstart_gui.md) if you want to play with the web-based interface.

Other relevant documents are:

* [The Listener Script - listen.py](listen_py.md) - how to use OpenRVDAS's core utility script
* [Configuration Files](configuration_files.md) - how to define configuration files to simplify running loggers with listen.py
* [OpenRVDAS Components](../_pages/components.md) - what components exist and what they do
* [Simulating Live Data](simulating_live_data.md) - using the simulate_data.py script to simulate a live system using stored data for development and testing
* [Grafana/InfluxDB-based Displays](grafana_displays.md) - an introduction to using InfluxDB and Grafana for displaying data
* [Parsing](parsing.md) - how to work with the included RecordParser to turn raw text records into structured data fields
* [Security assumptions](security.md) - the (rather naive) security assumptions made about the environment in which OpenRVDAS runs.

OpenRVDAS is a part of the [Ocean Data Tools project](http://oceandata.tools).
