---
permalink: /guide/operations/
title: "Operations and Recordkeeping"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
Running a real cruise: proving afterwards what ran and with which
configuration, controlling the system without the console, and letting
the ship's position drive logger changes so a watchstander doesn't have
to.

# Snapshots and the State Journal

*Not yet rewritten. In the meantime, see
[Recording What Ran: Snapshots and Journal]({{ "/cruise_records/" | relative_url }}).*

The state journal's running account of what the logger manager did;
`config_snapshot` and automatic snapshots (new in v2.7.0); archiving a
cruise; and pushing logger state changes into Sealog.

# Command-Line and API Control

*Not yet rewritten. In the meantime, see
[Controlling Loggers]({{ "/controlling_loggers/" | relative_url }}).*

Everything the console does, scriptably: `lmcmd`, the logger manager's
API, and driving mode changes from cron jobs and other systems.

# Geofencing and Conditional Control

*Not yet rewritten. In the meantime, see
[Geofencing and Automatic Logger Control]({{ "/geofencing/" | relative_url }}).*

The GeofenceTransform plus LoggerManagerWriter pattern: changing cruise
modes automatically when the ship crosses a boundary — leaving port,
entering an EEZ — and, more generally, letting the data itself drive
logger control.
