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
root access and no YAML. It is also the section to hand a new
watchstander.

It assumes someone has already installed OpenRVDAS (section
[3. Installation]({{ "/guide/installation/" | relative_url }})) and set up
a cruise definition for the vessel (section
[5. Setting Up Your Own Vessel]({{ "/guide/your-vessel/" | relative_url }})).
The screenshots use the NBP sample cruise that ships with OpenRVDAS —
your vessel will have different loggers and mode names, but the controls
are the same.

# The Web Console

Point a browser at the OpenRVDAS machine — `http://openrvdas`, or
whatever your installation's hostname is. You should see the console's
cruise management page:

![Initial web console](../../assets/images/nbp_initial.png)

Your installation runs one of OpenRVDAS's two consoles — Django or React
(see [How It Works]({{ "/guide/introduction/#how-it-works" | relative_url }})).
They look different but offer the same essential controls, and everything
in this section applies to both; as throughout the Guide, screenshots are
of the Django console.

Anyone can view the console; to change anything you must **log in** using
the link at the top of the page. On the Django console the account is
typically the OpenRVDAS user created at installation (`rvdas` on most
vessels); on the React console, accounts are managed from the console
itself by its admin user. If no cruise definition has been loaded yet,
logging in also gets you a "Load configuration file" button — more on
that below.

With a cruise definition loaded, the main page shows one row per logger.
Each row's button names the **logger configuration** that logger is
currently in — `gyr1->net`, `s330->off` — and its color tells you how the
logger is doing:

* **Green** — running normally.
* **Grey** — not running, as intended. A logger in its `off`
  configuration has nothing to do, and grey is its normal state.
* **Yellow** — starting up. Loggers pass through yellow for a few
  seconds after a mode change; a logger that *stays* yellow deserves
  attention.
* **Red** — failing: the logger has crashed, or is being restarted
  repeatedly without success. See
  [When Something Goes Red](#when-something-goes-red).

If every button turns red at once and the status timestamps at the top
of the page stop updating, the console has lost contact with the server
side — that's a different problem from every logger failing
simultaneously, and restarting loggers won't fix it. See
[When Something Goes Red](#when-something-goes-red).

# Starting and Stopping Loggers

In day-to-day operation you rarely touch individual loggers. Instead you
change the **cruise mode**: a mapping, defined in the cruise definition,
from each logger to the configuration it should be in when the ship is
in a particular situation. A typical vessel defines modes like `off`,
`port`, `EEZ` and `underway` — in `port` mode, for example, the weather
loggers might run while the Knudsen stays off. The NBP sample cruise
keeps it simpler:

* `off` — every logger off.
* `no_write` — every logger reads its instrument and broadcasts the
  data on the network, but writes nothing to disk.
* `write` — as `no_write`, and the data is also written to logfiles.
* `no_write+influx` and `write+influx` — as above, with parsed values
  also sent to the InfluxDB database, if one is installed.

To change the mode, select the mode button at the top of the logger
table. A dialog opens with a dropdown of the modes the cruise definition
offers (and a view of the logger manager's recent stderr, useful when
something misbehaves):

![Changing cruise mode](../../assets/images/nbp_change_mode.png)

Choose a mode and press "Change mode". Over the next few seconds each
logger switches to its configuration for that mode, passing through
yellow to green:

![Sample cruise running in no_write mode](../../assets/images/nbp_running.png)

To change a **single logger** — say, to turn one noisy instrument off
without disturbing the rest — select that logger's configuration button.
The dialog shows a dropdown of the configurations defined for that
logger, the logger's recent stderr output, and, at the bottom, the full
definition of the selected configuration:

![Selecting a logger configuration](../../assets/images/sample_cruise_select_logger_config.png)

An individually set logger keeps its configuration until the next mode
change, which puts every logger back in its configuration for the
chosen mode.

**Loading a cruise definition** is the one remaining control, and on
most vessels it happens once per cruise rather than once per watch.
After logging in, the "Load configuration file" button lets you choose
a cruise definition file; loading it populates the logger table and
puts the system in the definition's default mode (`off`, for the sample
cruise). Everything the console displays — loggers, configurations,
modes — comes from this file.

# Watching the Data: Displays

The console tells you whether loggers are running; it doesn't show you
the data they produce. For that, your installation may offer either or
both of:

* **Grafana dashboards** — the preferred route, if InfluxDB and Grafana
  are installed. These are typically served on port 3000 of the
  OpenRVDAS machine (`http://openrvdas:3000`), and show live and
  historical plots of any parsed field.

  ![Grafana dashboard](../../assets/images/grafana_dashboard.png)

* **Built-in display widgets** — web pages served by the console under
  `/display/`. With the sample cruise running, try
  `http://openrvdas/display/nbp_dashboard.html`:

  ![NBP widget dashboard](../../assets/images/nbp_dashboard.png)

  These widgets are fed live from the cached data server. They predate
  the Grafana route and are no longer the recommended one, but many
  vessels still use them.

Displays update only when loggers are running in a configuration that
feeds them — for the sample cruise, any mode other than `off`. A blank
display with green loggers usually means the system is in a mode that
isn't sending parsed data; a mode with parsing (for Grafana, an
`+influx` mode) fixes it. Section
[7. Storage, Displays and Distribution]({{ "/guide/storage-displays/" | relative_url }})
covers building and modifying displays.

# Where the Data Ends Up

Three places, with different lifetimes:

* **Logfiles** are the authoritative raw record. In modes that write to
  file, each logger appends every record it reads — raw, as it came
  from the instrument, plus a timestamp — to a file named for the
  logger with the current date appended (`seap-2026-10-28`), rolling
  over at midnight UTC. Where those files live is set in the cruise
  definition; the sample cruise writes under `/var/tmp/log/`, and your
  vessel will have its own convention.
* **The database** (InfluxDB, if installed) holds the parsed, named
  fields — `S330HeadingTrue`, `MwxAirTemp` — as time series, for
  Grafana and anything else that wants history.
* **The cached data server** holds only the latest values of each
  field, in memory, to feed live displays and derived-data loggers. It
  is not storage: its contents are gone on restart, which is fine,
  because the logfiles and the database are the records.

# When Something Goes Red

A red logger button means the logger is crashing: supervisor starts it,
it dies, and after repeated failures the system gives up. First-line
response, in order:

1. **Read its stderr.** Select the logger's configuration button; the
   dialog shows its recent stderr output, and the last few lines
   usually name the problem — a serial port that can't be opened, a
   full disk, a typo in a changed configuration.
2. **Restart it.** In the same dialog, re-select the configuration it
   should be in. If the cause was transient — an instrument that was
   power-cycled, a network blip — the logger comes back green and
   you're done.
3. **Rule out the system-wide case.** If *every* logger is red and the
   status timestamps at the top of the page are stale, the console has
   lost contact with the server side; individual loggers are probably
   fine. This needs someone with shell access — see
   [9. Troubleshooting]({{ "/guide/troubleshooting/" | relative_url }}).
4. **Write down what you saw** for the person you escalate to: which
   logger, which configuration, when it went red, the tail of its
   stderr, and anything that changed around that time (a mode change, a
   definition reload, an instrument being serviced).

A logger's stderr also goes to disk, where it survives console
restarts: from v2.7.0, at `/var/log/openrvdas/loggers/<logger>.stderr`
(earlier versions wrote `/var/log/openrvdas/<logger>.stderr`). The
files rotate, so the history is there when you come back to it. The
deeper diagnostic path — isolating a failing pipeline stage with
`listen`, checking supervisor itself — is in
[9. Troubleshooting]({{ "/guide/troubleshooting/" | relative_url }}).
