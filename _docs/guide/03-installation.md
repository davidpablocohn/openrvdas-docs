---
permalink: /guide/installation/
title: "Installation"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
How to get OpenRVDAS onto a machine: the standard installer (which is what
you want), the minimal alternative (for when you truly can't use the
installer), the optional InfluxDB/Grafana stack, securing the result, and
upgrading later.

# Standard Installation

*Not yet rewritten. In the meantime, see the
[Installation Guide]({{ "/install/" | relative_url }}).*

Running `utils/install_openrvdas.sh`, what each of its questions means —
including the choice between the Django and React consoles — and checking
that the result works.

> **Do you actually need a minimal installation?** Almost certainly not.
> The standard installer is the supported path and handles the services,
> users and permissions for you. Install minimally only if you need
> OpenRVDAS as a library on a machine that will never run the full system.

# The Python Virtual Environment

The installer creates a Python virtual environment at
`/opt/openrvdas/venv` (the exact path is printed at the end of
installation) and sets every OpenRVDAS service to run from it. Services
run under supervisor use it automatically; nothing needs activating for
the installed system to work.

To run OpenRVDAS commands by hand, though, activate the virtual
environment in your shell first — otherwise the commands won't be on
your path, and some of the Python packages they depend on won't be
available:

```
source /opt/openrvdas/venv/bin/activate
```

Your prompt gains a `(venv)` prefix, `python` now means the virtual
environment's Python, and the OpenRVDAS commands — `listen`,
`logger_manager`, `lmcmd`, `validate_config` and the rest — can be run
by name. Run them from the OpenRVDAS directory (e.g. `/opt/openrvdas`),
since relative paths in configurations and on the command line are
resolved against the current directory. Run `deactivate` to leave the
virtual environment.

Two conveniences worth knowing:

* For a one-off command you can skip activation by giving the command's
  path in the virtual environment, e.g. `venv/bin/listen ...`.
* The installer offers to add the activation line to the OpenRVDAS
  user's login script, so that user's shells start with the virtual
  environment already active.

# Minimal Installation

*Not yet rewritten. In the meantime, see the
[Installation Guide]({{ "/install/" | relative_url }}).*

Installing the OpenRVDAS package alone — no supervisor, no web console, no
database — for development machines and embedded uses.

# Sidebar: Choosing and Switching Between the Django and React Consoles

*Not yet rewritten. In the meantime, see
[Web Consoles: Django and React]({{ "/web_uis/" | relative_url }}).*

What each console requires, how the installer sets both up with one
active, and how `utils/switch_ui.sh` switches an installed system from one
to the other (new in v2.7.0).

# InfluxDB and Grafana

*Not yet rewritten. In the meantime, see
[Grafana/Influx-Based Displays]({{ "/grafana_displays/" | relative_url }}).*

Installing the time-series database and dashboard server alongside
OpenRVDAS, and wiring loggers to feed it.

# Securing the Installation

*Not yet rewritten. In the meantime, see
[Working with Secure Websockets]({{ "/secure_websockets/" | relative_url }}) and
[Security Assumptions]({{ "/security/" | relative_url }}).*

What OpenRVDAS assumes about the network it runs on, and setting up SSL
for the console and websockets.

# Upgrading an Existing Installation

*Not yet rewritten.*

Bringing an installed system up to a new release, and what changes between
releases that an upgrader needs to know — starting with v2.7.0's installed
command names and second console.
