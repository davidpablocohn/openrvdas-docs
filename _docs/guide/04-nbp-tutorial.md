---
permalink: /guide/nbp-tutorial/
title: "Tutorial: The NBP Sample Cruise"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
OpenRVDAS ships with a complete sample cruise — real sensor data recorded
aboard the R/V Nathaniel B. Palmer — that runs on any installation with no
hardware attached. This tutorial walks it end to end: simulate the ship's
sensors, load the cruise definition, watch the data flow, and poke at the
moving parts. Everything later in the Guide refers back to it.

# Simulating Live Data

*Not yet rewritten. In the meantime, see
[Simulating Live Data]({{ "/simulating_live_data/" | relative_url }}).*

Using `simulate_data` to replay the NBP's recorded sensor streams as if
the instruments were attached.

# Loading the Cruise Definition and Starting Loggers

*Not yet rewritten. In the meantime, see the
[Quickstart]({{ "/quickstart/" | relative_url }}) and
[GUI Quickstart]({{ "/quickstart_gui/" | relative_url }}).*

Loading `NBP1406_cruise.yaml` in the console, switching from `off` to an
active mode, and watching the loggers go green.

# Following a Record Through the System

*Not yet rewritten. In the meantime, see the
[Quickstart]({{ "/quickstart/" | relative_url }}).*

One gyroscope sentence, traced from simulated serial port through
timestamping, parsing and the cached data server to a logfile, the
database and a display.

# Exploring with listen

*Not yet rewritten. In the meantime, see
[The Listener Script]({{ "/listen_py/" | relative_url }}).*

Using `listen` to run a single logger configuration by hand, snoop on UDP
ports, and understand what each stage of a pipeline does — the habit that
pays off every time something breaks.
