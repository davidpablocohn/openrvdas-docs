---
permalink: /api_reference/
title: "API Reference"
layout: single
toc: true
toc_label: "Contents"
toc_icon: "list"
toc_sticky: true  # Makes the TOC stick on scroll
---
The **[OpenRVDAS API Reference]({{ "/api/" | relative_url }})** is the
automatically-generated documentation for every OpenRVDAS logger component and
server module: class signatures, constructor arguments, method docstrings and,
where useful, the source itself.

It is the same documentation that is installed alongside the code, so if you
already have OpenRVDAS on a machine you can also browse it offline by opening
`openrvdas/docs/html/index.html` in a browser.

## What's covered

The reference documents the two Python packages that make up a running
OpenRVDAS installation:

| Section | Contents |
| --- | --- |
| [Readers]({{ "/api/openrvdas/logger/readers.html" | relative_url }}) | Components that acquire data: serial ports, UDP/TCP sockets, files, databases, Redis, MQTT, Modbus and more. |
| [Transforms]({{ "/api/openrvdas/logger/transforms.html" | relative_url }}) | Components that parse, filter, reformat, derive or otherwise manipulate records in flight. |
| [Writers]({{ "/api/openrvdas/logger/writers.html" | relative_url }}) | Components that deliver records to files, databases, network sockets, InfluxDB, Grafana Live, email and elsewhere. |
| [Utils]({{ "/api/openrvdas/logger/utils.html" | relative_url }}) | Shared helpers: record formats, timestamps, NMEA/record parsing, and the DASRecord class. |
| [Listener]({{ "/api/openrvdas/logger/listener.html" | relative_url }}) | The machinery behind `listen.py`, which chains readers, transforms and writers together. |
| [Server]({{ "/api/openrvdas/server.html" | relative_url }}) | Logger manager, logger runner/supervisor, the cached data server, the websocket server and the server APIs. |

For a narrative introduction to how these fit together, start with
[Introduction to Loggers]({{ "/intro_to_loggers/" | relative_url }}) and
[OpenRVDAS Components]({{ "/components/" | relative_url }}); the API reference
is where you go once you know which component you want and need its exact
arguments.

## How it's generated

The reference is built with [pdoc](https://pdoc.dev/) directly from the
docstrings in the OpenRVDAS source tree, by `docs/generate_html_docs.sh` in the
[OpenRVDAS repository](https://github.com/OceanDataTools/openrvdas). That
repository regenerates it automatically when logger or server code changes, and
this site picks up the current `master` version each time it is rebuilt.

Because it is generated from source, the reference reflects the code rather than
this handbook: if a component's docstring is thin, the reference will be thin
too. Improvements are welcome as pull requests against the docstrings
themselves.

## Searching

Every page in the reference carries a search box that indexes the full API
across all modules, and the left-hand sidebar lists the classes and methods on
the page you are reading. The site search at the top of *this* page covers the
handbook only, so use the reference's own search when you are looking for a
class or argument name.
