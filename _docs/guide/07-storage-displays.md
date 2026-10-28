---
permalink: /guide/storage-displays/
title: "Storage, Displays and Distribution"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
Where the data goes once a logger has it: the cached data server that
feeds everything live, the database that keeps history, the displays
people actually look at, and spreading the load across machines and to
shore.

# The Cached Data Server

*Not yet rewritten. In the meantime, see
[The Cached Data Server]({{ "/cached_data_server/" | relative_url }}).*

What the CDS holds, its websocket subscription protocol, and its role as
the hub between loggers, displays and derived-data computations.

# The Database

*Not yet rewritten. In the meantime, see
[Grafana/Influx-Based Displays]({{ "/grafana_displays/" | relative_url }}).*

Writing parsed fields to InfluxDB, retention, and reading the data back
out for other tools.

# Displays

*Not yet rewritten. In the meantime, see
[Display Widgets]({{ "/display_widgets/" | relative_url }}),
[Grafana/Influx-Based Displays]({{ "/grafana_displays/" | relative_url }}) and
[Grafana Live]({{ "/grafana_live/" | relative_url }}).*

The built-in display widgets, Grafana dashboards over InfluxDB, and
Grafana Live for sub-second updates straight from the CDS.

# Shoreside Replication

*Not yet rewritten. In the meantime, see
[InfluxDB Shoreside Replication]({{ "/cookbook/influxdb_shoreside_replication/" | relative_url }}).*

Mirroring the ship's InfluxDB to shore over an intermittent satellite
link, so shoreside dashboards lag the ship instead of breaking.

# Distribution and Load Balancing

*Not yet rewritten.*

Running OpenRVDAS across several machines: remote logger runners, where
the CDS and database should live, and patterns for splitting acquisition
from display on busy installations.
