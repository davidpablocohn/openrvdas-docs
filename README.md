# OpenRVDAS Documentation



OpenRVDAS (Open Research Vessel Data Acquisition System) is an open source software framework for building custom data acquisition systems. It is designed for oceanographic research vessels and other science platforms that need to record streaming data from serial ports, network-aware sensors, and other sources.

## Where to start?
* [OpenRVDAS Quickstart](quickstart.md) if you want to just grab the code and poke around with basic loggers as quickly as possible.
* [GUI Quickstart](quickstart_gui.md) if you want to play with the web-based interface.

Other relevant documents are:

* [The Listener Script - listen.py](listen_py.md) - how to use OpenRVDAS's core utility script
* [Configuration Files](configuration_files.md) - how to define configuration files to simplify running loggers with listen.py
* [OpenRVDAS Components](components.md) - what components exist and what they do
* [Simulating Live Data](simulating_live_data.md) - using the simulate_data.py script to simulate a live system using stored data for development and testing
* [Grafana/InfluxDB-based Displays](grafana_displays.md) - an introduction to using InfluxDB and Grafana for displaying data
* [Parsing](parsing.md) - how to work with the included RecordParser to turn raw text records into structured data fields
* [Security assumptions](security.md) - the (rather naive) security assumptions made about the environment in which OpenRVDAS runs.

---

## This Repository

This repository contains the source for the OpenRVDAS documentation site, built with [Jekyll](https://jekyllrb.com/) using the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme and hosted via GitHub Pages.

See [install.md](install.md) for instructions on running the documentation site locally.

## Links

- **OpenRVDAS GitHub Repository:** https://github.com/OceanDataTools/openrvdas
- **Live Documentation Site:** https://oceandatatools.github.io/openrvdas-docs/
