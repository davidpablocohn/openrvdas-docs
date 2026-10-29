---
permalink: /guide/operations/
title: '8\. Operations and Recordkeeping'
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
The earlier sections were about setting a system up. This one is about
running it through a real cruise:

* keeping a record of what ran, so questions can be answered months
  later;
* controlling the system from the command line or from other
  programs, without the web console;
* letting the ship's position, or the data itself, change logger
  configurations automatically.

# Snapshots and the State Journal

Data is only as useful as what is known about how it was collected.
Months after a cruise, someone will ask questions like these:

* Which calibration coefficients were applied to the TSG?
* Were the true winds computed from the port or the starboard
  anemometer?
* Why is there a gap in the gravimeter record at 0300 on day 12?

OpenRVDAS v2.7.0 added three tools for answering them:

* the **state journal**, a running log of everything the logger
  manager does;
* **`config_snapshot`**, a command that saves a complete copy of a
  configuration;
* **automatic snapshots**, which the logger manager takes whenever the
  configuration changes.

## The state journal

The logger manager keeps a journal of everything it does. It's on by
default from v2.7.0. The journal records:

* each cruise definition that is loaded;
* each change of cruise mode;
* each logger that is started, stopped, switched to a different
  configuration, crashes, recovers, or is given up on.

Each entry gives the time, the logger and configuration involved, and
the version of the OpenRVDAS code the logger was running. If someone
had edited the code without committing the change, the version shows
that too, so you can tell when a transform was patched mid-cruise.

The journal is written as one file per day (UTC), named
`/var/log/openrvdas/logger_manager_journal-YYYY-MM-DD`. Each line of
the file is one event in JSON. A change of mode looks like this
(it's a single line in the file):

```
{"data_id": "logger_manager", "message_type": "mode_changed", "timestamp": 1792677791.204,
 "fields": {"event": "mode_changed", "time": "2026-10-22T14:03:11.204Z", "from": "no_write", "to": "write"}}
```

A logger that keeps crashing won't fill the journal. Only its first
crash is recorded, and the total number of crashes is recorded when
the logger recovers, fails or is stopped. And the journal can never
interfere with running loggers: if the logger manager can't write it,
it logs a warning and carries on.

Since each line is plain JSON, you can search the journal with `jq` or
`grep`:

```
# Every mode change, in order
jq -r 'select(.message_type=="mode_changed")
       | "\(.fields.time)  \(.fields.from) -> \(.fields.to)"' \
   /var/log/openrvdas/logger_manager_journal-*

# Everything that happened to the gyro logger
grep '"logger": "gyr1"' /var/log/openrvdas/logger_manager_journal-*
```

The journal uses the same format as the logfiles a `LogfileWriter`
writes. That means a logger can read it with a `LogfileReader`, just
as it would read instrument data. The
[Sealog example](#logger-events-in-sealog) below uses this.

To move the journal or turn it off, use the logger manager's
`--state_journal` argument (`--state_journal none` turns it off). The
full list of journal events is on the legacy
[Recording What Ran]({{ "/cruise_records/" | relative_url }}) page.

## Taking a snapshot

The journal records what happened. A snapshot records what the
configuration was. To take one of a running system:

```
cd /opt/openrvdas
config_snapshot --output /var/log/openrvdas/snapshots
```

`config_snapshot` will look in the journal to find the cruise
definition that is currently loaded, and snapshot that. It will print
the location of the snapshot, a directory named after the cruise id
and the time. A few variations:

* Add `--tar` to also get the snapshot as a single `.tar.gz` file,
  handy for attaching to a report.
* Name a cruise definition file to snapshot that file instead, whether
  or not it's loaded. This is useful for recording what you're about
  to sail with.

A snapshot directory contains:

```
MVP2610_20261023T212317Z/
  MANIFEST.yaml                 what was captured, and from where
  expanded_config.yaml          the fully expanded cruise definition, secrets redacted
  logger_manager_journal.jsonl  the journal since the logger manager last started
  sources/                      every file the definition was built from
  patches/                      "git diff HEAD" of any repository with uncommitted changes
```

What each part is for:

* **`sources/`** has a copy of every file the cruise definition was
  built from: the definition itself, the templates and calibration
  files it includes, and the device definitions its parsers use. With
  these, the configuration can be loaded again later, exactly as it
  was.
* **`expanded_config.yaml`** is the cruise definition with every
  include, template and variable filled in. It's exactly what the
  logger manager saw, and usually the quickest way to answer "what was
  this logger actually doing?"
* **`MANIFEST.yaml`** records the versions of everything involved:
  OpenRVDAS, your
  [institution's repository]({{ "/guide/your-vessel/#your-institutions-repository-and-local" | relative_url }}),
  the operating system, Python and every installed package. It also
  records what state each logger was in when the snapshot was taken.

That last item is often the most useful. For each logger, the manifest
says which configuration it was running, whether it was running
normally, crashing or stopped, and whether its configuration matches
the definition file on disk. If someone edits a calibration file and
forgets to reload the definition, the running loggers are still using
the old values, and the snapshot will warn you:

```
WARNING: These files have changed since the definition was loaded, so may not match what
is running: sources/local/uuw/mvp/calibrations.yaml
WARNING: These loggers are running configs that differ from this definition: tsg_cal
```

If a file is a symbolic link, such as a `calibrations.yaml` that
points to a dated calibration file, the snapshot saves the contents of
the file it points to and notes that file's name in the manifest. So
the [dated calibration files]({{ "/guide/computed-values/#calibrations" | relative_url }})
convention leaves an exact record of which coefficients were in use.

**A caution about secrets.** In `expanded_config.yaml`, anything that
looks like a password, token or API key is replaced with
`<redacted>`. The files in `sources/` are copied unchanged, though, so
that they can be loaded again. If any of them seem to contain a
secret, `config_snapshot` will warn you and name the files. Check
before sending a snapshot off the ship.

## Automatic snapshots

You don't have to remember to take snapshots. The logger manager can
take them for you, and it will do so at two moments:

* whenever a cruise definition is loaded or reloaded;
* whenever one of the files the definition was built from changes,
  such as a calibration file or a logger template.

Checking for changed files costs almost nothing, and snapshots are
written in the background, so turning this on won't slow the system
down. Each one is about 200 KB for the sample NBP cruise. They're
worth having on any real installation.

The installer asks whether you want automatic snapshots, and where to
keep them. If you said no and change your mind, rerun the installer
and say yes. The setting is the logger manager's `--snapshot_dir`
argument, for example `--snapshot_dir /var/log/openrvdas/snapshots`.

To check that it's working, load a cruise definition. A new snapshot
directory should appear, and the journal should record it:

```
ls -t /var/log/openrvdas/snapshots | head -1
grep snapshot_ /var/log/openrvdas/logger_manager_journal-$(date -u +%F) | tail -1
```

The journal line will say `snapshot_taken` if all went well. If it
says `snapshot_failed`, its `error` field gives the reason. The usual
cause is that the OpenRVDAS user isn't allowed to write to the
snapshot directory.

## Archiving a cruise

At the end of a cruise, save a record that will still answer
questions after the system has been set up for the next cruise. Put
these next to the cruise's data:

1. **A final snapshot**, taken before anything is shut down or
   changed.
2. **All the automatic snapshots** from the cruise. Together they
   show every change to the configuration, as it happened.
3. **The whole journal.** Each snapshot includes the journal only
   since the logger manager last started, and it may have been
   restarted during the cruise. The journal files are small, so copy
   them all.
4. **The loggers' stderr files**, from `/var/log/openrvdas/loggers/`.
   The journal tells you *that* a logger crashed at 0300; its stderr
   file usually tells you *why*. Older stderr files are eventually
   deleted, so copy them before that happens.
5. **A tag in your institution's repository**, such as
   `git tag MVP2610-end`, so the configuration can be checked out
   later exactly as it was.

Steps 1 to 4 as commands:

```
CRUISE=MVP2610
ARCHIVE=/data/$CRUISE/openrvdas_records
mkdir -p $ARCHIVE/snapshots $ARCHIVE/journal $ARCHIVE/logger_stderr

config_snapshot --output $ARCHIVE --tar
cp -a /var/log/openrvdas/snapshots/${CRUISE}_* $ARCHIVE/snapshots/
cp -a /var/log/openrvdas/logger_manager_journal-* $ARCHIVE/journal/
cp -a /var/log/openrvdas/loggers/. $ARCHIVE/logger_stderr/
```

For a quick record partway through a cruise, step 1 alone is enough.
One snapshot captures the configuration, the code version and the
state of every logger.

## Logger events in Sealog

If your ship runs [Sealog](https://github.com/OceanDataTools/sealog-server),
it helps to have mode changes and logger failures appear in its event
log. A watchstander looking back through the night's events will then
see "mode changed to underway" or "gravimeter logger failed" alongside
everything else that happened.

Because a logger can read the journal, an ordinary logger can do this.
It needs three components:

* a **`LogfileReader`** that follows the journal as it grows;
* a **[`ComputedFieldsTransform`]({{ "/guide/computed-values/#computed-fields" | relative_url }})**
  that picks out the events you want and turns each one into the
  fields a Sealog event needs, dropping all the others;
* a **`SealogWriter`** that posts the events to the Sealog server.

Two things to get right:

* Give this logger the same configuration in every cruise mode. When a
  logger restarts, it rereads the journal from the beginning and posts
  those events again. A logger whose configuration doesn't change
  won't be restarted by a mode change.
* The `SealogWriter` needs an access token. Keep it in a separate
  included file that isn't committed to your repository.

The complete logger configuration is on the legacy
[Recording What Ran]({{ "/cruise_records/#creating-sealog-events-from-logger-state-changes" | relative_url }})
page.

# Command-Line and API Control

Anything you can do in the web console, you can also do from the
command line or from another program. There are three ways.

**`lmcmd`** sends commands to the running logger manager. It takes the
same commands the console uses:

```
lmcmd load_configuration local/uuw/mvp/MVP2610_cruise.yaml
lmcmd get_modes
lmcmd set_active_mode underway
lmcmd get_logger_configs gyr1
lmcmd set_active_logger_config gyr1 gyr1-off
```

Run it with no arguments for an interactive `command?` prompt, where
`help` lists every command. `lmcmd` is useful:

* on an installation with no web console;
* for a cron job that changes the mode at a set time;
* when the console is down and you still need to control the loggers.

`lmcmd` works with the Django console's database. With the React
console, use its API instead.

**The REST API** lets other programs control the logger manager.
The Django console provides endpoints such as
`api/select-cruise-mode/`, `api/load-configuration-file/` and
`api/edit-logger-config/`. You can browse and try them all at
`/api/schema/swagger-ui/`. They require the same login as the console.
The React console has its own API, documented at `/docs` and `/redoc`
if you chose to make those pages available when you installed it.

To *watch* the system from a program, subscribe to the cached data
server. The logger manager publishes the state of the cruise and of
every logger there, in the `status:cruise_definition` and
`status:logger_status` fields, and each logger's error output appears
in `stderr:` fields. This is how the console itself gets its status.
The legacy [Controlling Loggers]({{ "/controlling_loggers/" | relative_url }})
page lists all the endpoints, and shows how to add your own.

**The logger manager can also be run by hand**, which is handy on a
test machine:

```
logger_manager --config local/uuw/mvp/MVP2610_cruise.yaml --mode port
```

This loads the definition and sets the mode. Run this way, the logger
manager keeps its state in memory and gives you its own `command?`
prompt. A few of its other arguments are worth knowing:

* `--state_journal` sets where the journal is written;
* `--snapshot_dir` turns on automatic snapshots;
* `--stderr_file_pattern` sets where each logger's error output goes.
  The default is `/var/log/openrvdas/loggers/{logger}.stderr`. Each
  file is rotated when it reaches 1 MB, and up to 100 older files are
  kept.

# Geofencing and Conditional Control

Some mode changes depend on where the ship is. You might start logging
as the ship leaves port, stop recording some instruments on entering
a foreign country's waters, and start again on leaving. A watchstander
has to remember to make each of these changes, often at an
inconvenient hour.

OpenRVDAS can make them automatically. A command to the logger
manager, such as `set_active_mode underway`, is just a piece of text,
and a logger can write it like any other record. So a logger can
watch the data and change the mode when it sees the right condition.

Such a logger has three parts:

* a reader that receives the parsed data;
* a transform that outputs a command when a condition is met;
* a **`LoggerManagerWriter`**, which passes the command to the logger
  manager.

For geofencing, the transform is a `GeofenceTransform`:

```
readers:
  class: UDPReader
  kwargs:
    port: 6224

transforms:
  - class: GeofenceTransform
    module: logger.transforms.geofence_transform
    kwargs:
      latitude_field_name: S330Latitude
      longitude_field_name: S330Longitude
      boundary_file_name: local/uuw/mvp/boundaries/argentina_eez.gml
      entering_boundary_message: set_active_mode eez
      leaving_boundary_message: set_active_mode underway

writers:
  - class: LoggerManagerWriter
    module: logger.writers.logger_manager_writer
    kwargs:
      database: django
      allowed_prefixes:
        - 'set_active_mode '
        - 'sleep '
```

Here's what happens:

1. The `GeofenceTransform` reads the ship's latitude and longitude
   from each record and compares the position with the boundary.
2. When the ship crosses into the boundary, it outputs
   `set_active_mode eez`. When the ship crosses out, it outputs
   `set_active_mode underway`. The rest of the time it outputs
   nothing.
3. The `LoggerManagerWriter` passes the command to the logger manager,
   which will change the mode. The change is recorded in the journal
   like any other.

Boundary files are in GML format. EEZ boundaries can be downloaded
from [marineregions.org](https://marineregions.org/eezsearch.php).

Some options worth knowing:

* **`distance_from_boundary_in_degrees`** moves the fence inside the
  boundary (negative values) or outside it, so the mode changes a
  little before the ship reaches the line. The distance is in degrees
  rather than nautical miles because converting between the two
  depends on where you are.
* **`seconds_between_checks`** limits how often the position is
  checked, to save work on a fast GPS feed.
* **`boundary_dir_name`** uses every `.gml` file in a directory, with
  the fence around all of them together. One way to use it: keep all
  the EEZ files you might need in one directory, and link the ones in
  force into another. To change the fence, add or remove a link, then
  switch the geofence logger `off` and back `on`.
* **`allowed_prefixes`** on the writer is a safety check. Only commands
  that start with one of these prefixes are passed to the logger
  manager. In this example, the logger can change the mode and nothing
  else.

The writer also accepts several commands in one record, separated by
semicolons, and a `sleep N` command that waits N seconds between
them.

Before using the `GeofenceTransform`, install the packages it needs.
They aren't installed by default. With the virtual environment active,
from the OpenRVDAS directory:

```
pip install -e '.[geofence]'
```

Note that the configuration names a `module:` for both components.
`listen` doesn't load them automatically.

**The same approach works with any field, not just position.** The
`QCFilterTransform` outputs a command when a field goes outside a
range you set. This one declares the ship underway once its speed is
over half a knot:

```
transforms:
  - class: QCFilterTransform
    kwargs:
      bounds: 'S330SpeedKt:0.0:0.5'
      message: set_active_mode underway
```

`bounds` gives the *normal* range for a field, as
`field:lowest:highest`. You can list several fields, separated by
commas. When a value goes outside its range, the transform outputs the
message.

Two things to be aware of:

* It only works in one direction. To switch back when the ship slows
  down, add a second logger with the opposite range.
* Unlike the `GeofenceTransform`, which speaks only when the ship
  crosses a boundary, the `QCFilterTransform` outputs its message for
  *every* record that is out of range. Here, that means the logger
  manager will be told to set `underway` mode with every GPS record
  for as long as the ship is moving. Each time, every logger is put
  back into its configuration for that mode. So if a watchstander
  switches one logger off by hand, it won't stay off. Use this
  approach only where that's acceptable.

For more complicated rules, use a
[`ComputedFieldsTransform`]({{ "/guide/computed-values/#computed-fields" | relative_url }})
whose equation produces the command when its condition is met, and
nothing otherwise. The `LoggerManagerWriter` works the same way
whichever transform feeds it.
