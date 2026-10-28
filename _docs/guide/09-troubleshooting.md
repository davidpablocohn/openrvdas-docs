---
permalink: /guide/troubleshooting/
title: '9\. Troubleshooting'
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
When something breaks, in rough order of usefulness: where the evidence
is, the failures everyone eventually hits, how to isolate a problem to
one stage of one logger, and the monitoring that tells you about trouble
before the science party does.

# Where to Look

*Not yet rewritten.*

Logger stderr (in the console, and on disk — where it lives from v2.7.0
onward, and where it went before), the logger manager's own logs,
supervisor state, and the state journal.

# Common Failure Modes

*Not yet rewritten.*

Serial port permissions, a parser that silently matches nothing, a
full disk, a wedged websocket, the CDS and console disagreeing, and the
other usual suspects — each with its symptom, diagnosis and fix.

# Isolating Problems with listen

*Not yet rewritten. In the meantime, see
[The Listener Script]({{ "/listen_py/" | relative_url }}) and
[Simulating Live Data]({{ "/simulating_live_data/" | relative_url }}).*

Rebuilding a failing pipeline one stage at a time with `listen`, and
substituting `simulate_data` for the hardware to decide whether the
problem is the instrument or the configuration.

# Monitoring Feed Health

*Not yet rewritten. In the meantime, see the
[Grafana Feed Status Dashboard]({{ "/cookbook/grafana_feed_status_dashboard/" | relative_url }}).*

A Grafana dashboard that tracks every feed arriving in InfluxDB,
flags the ones that have gone quiet, and adjusts itself as instruments
come and go.
