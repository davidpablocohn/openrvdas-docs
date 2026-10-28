---
permalink: /guide/running-system/
title: "Working with a Running Installation"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
Most people meet OpenRVDAS already running on a ship. This section is the
operator's view — how to use the system through its web console, with no
root access and no YAML. It is also the section to hand a new watchstander.

# The Web Console

*Not yet rewritten. In the meantime, see the
[GUI Quickstart]({{ "/quickstart_gui/" | relative_url }}) and
[Web Consoles: Django and React]({{ "/web_uis/" | relative_url }}).*

Logging in, reading the logger status page, and finding your way around —
in both the Django and React consoles.

# Starting and Stopping Loggers

*Not yet rewritten. In the meantime, see the
[GUI Quickstart]({{ "/quickstart_gui/" | relative_url }}) and
[Controlling Loggers]({{ "/controlling_loggers/" | relative_url }}).*

Cruise modes and what changing one does; starting, stopping and switching
the configuration of an individual logger; loading a new cruise definition.

# Watching the Data: Displays

*Not yet rewritten. In the meantime, see
[Display Widgets]({{ "/display_widgets/" | relative_url }}) and
[Grafana/Influx-Based Displays]({{ "/grafana_displays/" | relative_url }}).*

The console's built-in displays, and where to find the Grafana dashboards
if your installation has them.

# Where the Data Ends Up

*Not yet rewritten. In the meantime, see the
[Quickstart]({{ "/quickstart/" | relative_url }}).*

Logfiles on disk, the database, and how the day's files are organized.

# When Something Goes Red

*Not yet rewritten. In the meantime, see
[Troubleshooting]({{ "/guide/troubleshooting/" | relative_url }}).*

First-line response to a failed logger: reading its stderr in the console,
the restart that usually works, and what to write down for the person you
escalate to.
