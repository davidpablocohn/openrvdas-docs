---
permalink: /guide/operations/
title: '8\. Operations and Recordkeeping'
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
This section is about running a real cruise, as distinct from
configuring one:

* proving, months later, what ran and with which configuration;
* controlling the system without the console, from scripts and other
  systems;
* letting the ship's position, or the data itself, drive logger
  changes so a watchstander doesn't have to.

# Snapshots and the State Journal

Data is only as useful as what is known about how it was collected.
Months after a cruise, someone will ask which calibration
coefficients were applied to the TSG, whether the true winds came
from the port or starboard anemometer, or why there is a gap in the
gravimeter record at 0300 on day 12. OpenRVDAS v2.7.0 added three
tools for answering those questions: a **state journal** the logger
manager keeps as it runs, a **`config_snapshot`** command that
captures a configuration in full, and **automatic snapshots** taken
whenever the configuration changes.

## The state journal

From v2.7.0, the logger manager keeps a journal by default: one file
per UTC day at `/var/log/openrvdas/logger_manager_journal-YYYY-MM-DD`,
one JSON line per event. It records definitions loaded, mode
changes, and every logger started, stopped, switched, crashed,
recovered or given up on — each with the time, the logger and
configuration involved, and the version of the code the logger was
started with (as `git describe` reports it, with a `-dirty` marker
and hash if the working tree had uncommitted edits, so a transform
patched mid-cruise is distinguishable from the release). A change of
mode looks like this (unwrapped in the file):

```
{"data_id": "logger_manager", "message_type": "mode_changed", "timestamp": 1792677791.204,
 "fields": {"event": "mode_changed", "time": "2026-10-22T14:03:11.204Z", "from": "no_write", "to": "write"}}
```

Two design points keep it useful. Crashes are counted, not listed —
a logger failing in a loop journals its first crash and reports the
total when it recovers, fails or is stopped, so a noisy serial port
can't fill the journal. And journaling can never get in the way of
managing loggers: if the directory isn't writable, the logger manager
logs one warning and carries on.

Because each line is plain JSON, `jq` and `grep` work directly on it:

```
# Every mode change, in order
jq -r 'select(.message_type=="mode_changed")
       | "\(.fields.time)  \(.fields.from) -> \(.fields.to)"' \
   /var/log/openrvdas/logger_manager_journal-*

# Everything that happened to the gyro logger
grep '"logger": "gyr1"' /var/log/openrvdas/logger_manager_journal-*
```

The journal is written in the same format and file naming as
`LogfileWriter` output, so a `LogfileReader` can read and follow it —
which makes the journal a data stream any logger can consume. The
[Sealog integration](#logger-events-in-sealog) below is built on
exactly that. The journal's location is set by the logger manager's
`--state_journal` argument (`none` turns it off); the full event
catalogue is on the legacy
[Recording What Ran]({{ "/cruise_records/" | relative_url }}) page.

## Taking a snapshot

The journal says *what happened*; a snapshot captures *what the
configuration was*. On a running system:

```
cd /opt/openrvdas
config_snapshot --output /var/log/openrvdas/snapshots
```

With no definition named, `config_snapshot` asks the journal which
definition the logger manager loaded most recently and snapshots
that — a record of what is running now. It will print the path of
the snapshot it wrote, a directory named for the cruise id and the
UTC time; `--tar` also writes a `.tar.gz` beside it for attaching to a
report. Naming a cruise definition file instead snapshots that
definition whether or not it's loaded, for example to record what
you're about to sail with.

A snapshot contains:

```
MVP2610_20261023T212317Z/
  MANIFEST.yaml                 what was captured, and from where
  expanded_config.yaml          the fully expanded cruise definition, secrets redacted
  logger_manager_journal.jsonl  the journal since the logger manager last started
  sources/                      every file the definition was built from
  patches/                      "git diff HEAD" of any repository with uncommitted changes
```

`sources/` is the part that makes the snapshot reloadable: the cruise
definition, every file it includes (templates, calibration files),
every device definition file its parsers use, and any logfile header
files, each at its path relative to the OpenRVDAS directory.
`expanded_config.yaml` is the definition after every include,
template and variable has been resolved — exactly what the logger
manager saw, and usually the quickest answer to "what exactly was
this logger doing?" And `MANIFEST.yaml` records the OpenRVDAS
version; the commit, branch and dirty state of every repository a
file came from (OpenRVDAS itself and your
[institution's repository]({{ "/guide/your-vessel/#your-institutions-repository-and-local" | relative_url }}));
the OS, Python and every installed package; a sha256 for every
captured file; and, replayed from the journal, the state of every
logger at the moment of the snapshot.

That last part is where a snapshot earns its keep. For each logger it
records the configuration running, whether it is `running`,
`crashing`, `failed` or `stopped`, the code version it started with,
and `matches_definition` — whether what's running is identical to
what's in the definition file now. Edit a calibration file, or
repoint its symlink, without reloading the definition, and the next
snapshot will say so:

```
WARNING: These files have changed since the definition was loaded, so may not match what
is running: sources/local/uuw/mvp/calibrations.yaml
WARNING: These loggers are running configs that differ from this definition: tsg_cal
```

Symlinked files are captured under the name the definition used, with
the contents of the file they pointed to, and the manifest records
the real file as `resolves_to` — so the
[dated calibration files]({{ "/guide/computed-values/#calibrations" | relative_url }})
convention leaves a precise trail.

One caution: `expanded_config.yaml` has anything resembling a
password, token or API key replaced with `<redacted>`, but the files
under `sources/` are copied byte for byte so that they stay
reloadable. If any of them appear to contain a secret,
`config_snapshot` will warn you and name them. Bear that in mind
before a snapshot leaves the ship.

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

At the end of a cruise, the goal is a self-contained record that
will still answer questions after the system has been reconfigured
for the next one. Collect, next to the data:

1. **A final snapshot of what is running**, before anything is shut
   down: `config_snapshot --output $ARCHIVE --tar`.
2. **Every automatic snapshot** taken during the cruise — together
   they record each configuration change as it happened.
3. **The whole journal.** A snapshot includes only the journal since
   the logger manager last started, and it may have restarted several
   times; the daily files are tiny, so copy them all.
4. **The loggers' stderr files** from `/var/log/openrvdas/loggers/`.
   The journal says *that* the gravimeter logger crashed at 0300; its
   stderr usually says *why*. They rotate, so copy them before they're
   overwritten.
5. **A tag in your institution's repository** (`git tag MVP2610-end`),
   so the configuration can be checked out exactly as it was.

```
CRUISE=MVP2610
ARCHIVE=/data/$CRUISE/openrvdas_records
mkdir -p $ARCHIVE/snapshots $ARCHIVE/journal $ARCHIVE/logger_stderr

config_snapshot --output $ARCHIVE --tar
cp -a /var/log/openrvdas/snapshots/${CRUISE}_* $ARCHIVE/snapshots/
cp -a /var/log/openrvdas/logger_manager_journal-* $ARCHIVE/journal/
cp -a /var/log/openrvdas/loggers/. $ARCHIVE/logger_stderr/
```

For a quick record partway through a cruise, step 1 alone captures
the configuration, the code version and the current state of every
logger.

## Logger events in Sealog

If your ship runs [Sealog](https://github.com/OceanDataTools/sealog-server),
mode changes and logger failures belong in the event log next to
everything else, where a watchstander scrolling back through the
night sees "mode changed to underway" and "gravimeter logger failed"
in context. Since the journal is a data stream, a logger does this
with three components: a `LogfileReader` that follows the journal
(`tail: true`, `refresh_file_spec: true` to roll over to each new
day's file), a
[`ComputedFieldsTransform`]({{ "/guide/computed-values/#computed-fields" | relative_url }})
whose rules pick out the events of interest and shape their fields
into Sealog's `event_value`, `event_free_text` and `event_option_*`
fields — returning `None` for everything else, so that with
`delete_other_fields: true` uninteresting events are dropped
entirely — and a `SealogWriter` that posts the result. Give this
logger the same configuration in every mode, so mode changes don't
restart it (a restart replays the journal from the beginning), and
keep its Sealog token in an included file that isn't committed. The
complete logger, with its rules, is on the legacy
[Recording What Ran]({{ "/cruise_records/#creating-sealog-events-from-logger-state-changes" | relative_url }})
page.

# Command-Line and API Control

Everything the console does, the logger manager will also do from a
command line or a program. Three routes:

**`lmcmd`** connects to the running logger manager's database and
takes the same commands the console issues:

```
lmcmd load_configuration local/uuw/mvp/MVP2610_cruise.yaml
lmcmd get_modes
lmcmd set_active_mode underway
lmcmd get_logger_configs gyr1
lmcmd set_active_logger_config gyr1 gyr1-off
```

Run with no arguments it opens an interactive `command?` prompt;
`help` lists every command. This is the operator's tool for a
headless installation, for a cron job that switches modes at a
scheduled time, and for recovering a system whose console is down.
Note that `lmcmd` speaks to the logger manager through the Django
console's database (`--database django`, the default, or `sqlite`);
under the React console the equivalent is its API.

**The REST API** is the route for other systems. The Django console
exposes endpoints for loading and reloading definitions, selecting
modes and editing logger configurations —
`api/select-cruise-mode/`, `api/load-configuration-file/`,
`api/edit-logger-config/` and the rest, with a browsable schema at
`/api/schema/swagger-ui/` — behind the same authentication as the
console. The React console's FastAPI back end has its own API, with
live documentation at `/docs` and `/redoc` if you told the installer
to expose them. Status comes back the other way, through the cached
data server: the logger manager publishes `status:cruise_definition`
and `status:logger_status` fields there, and loggers' stderr arrives
as `stderr:` fields, so any subscriber can watch the system as the
console does. The legacy
[Controlling Loggers]({{ "/controlling_loggers/" | relative_url }})
page lists the endpoints and shows how to add your own.

**The logger manager itself** can be run by hand, with a definition
and mode on its command line, for a test machine or a one-off:

```
logger_manager --config local/uuw/mvp/MVP2610_cruise.yaml --mode port
```

With no `--database`, it keeps its state in memory and offers its own
`command?` console; the installed service runs it with `--no-console`
and the console's database instead. Its other arguments of
operational interest are `--state_journal`, `--snapshot_dir` and
`--stderr_file_pattern`, which places each logger's stderr (default
`/var/log/openrvdas/loggers/{logger}.stderr`, rotated at 1 MB with up
to 100 older files kept).

# Geofencing and Conditional Control

Changing logger configurations as the ship moves is routine and
error-prone: start logging as the ship leaves port, stop recording
restricted instruments on entering a foreign EEZ, start again on
leaving. Each is a mode change that a watchstander has to remember,
at an hour nobody chose. The same components that move data can make
the change automatically — because to OpenRVDAS, a command to the
logger manager is just another record a logger can write.

The pattern is a logger whose reader watches the parsed data, whose
transform emits a command when a condition is met, and whose writer
is a `LoggerManagerWriter` that passes the command to the logger
manager. For geofencing, the transform is `GeofenceTransform`:

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

The transform watches the stream for records carrying the named
latitude and longitude fields, compares each position with the
boundary, and emits a message only when the position has *crossed*
it since the last record — entering, or leaving. The writer checks
each message against `allowed_prefixes` and, if it passes, issues it
to the logger manager as a command. So crossing into the EEZ will
switch the system to `eez` mode and crossing out will switch it back
to `underway`, each change journaled like any other. Boundary files
are GML polygons; EEZ boundaries can be downloaded from
[marineregions.org](https://marineregions.org/eezsearch.php).

Details that matter in practice:

* **`distance_from_boundary_in_degrees`** moves the fence inward
  (negative) or outward from the boundary, giving a buffer so the
  change happens before the line rather than on it. It is in
  degrees, deliberately: a distance in nautical miles would need a
  projection that changes with position.
* **`seconds_between_checks`** limits how often the position is
  tested, which keeps the cost negligible on a 10 Hz GPS feed.
* **`boundary_dir_name`** takes a directory of `.gml` files and fences
  their union. Keeping every EEZ you might need in one directory and
  symlinking the ones currently in force into another makes updating
  the fence a matter of adding or removing a link and cycling the
  geofence logger `off` and back `on`.
* **`allowed_prefixes`** on the writer is the safety catch: only
  commands matching the list reach the logger manager, so a stray
  record can't do anything but change modes. Several commands can
  share one record, separated by semicolons, and `sleep N` pauses
  between them to let a change settle.
* The transform depends on packages that neither the standard
  installer nor a minimal installation includes. Install the
  `geofence` extra once, with the virtual environment active:
  `pip install -e '.[geofence]'` from the OpenRVDAS directory. Both
  components also need `module:` named, as they aren't among the
  defaults `listen` imports.

The same pattern works on any field, not just position. The
`QCFilterTransform` emits a message when a field leaves a stated
range — here, declaring the ship underway once it moves faster than
half a knot:

```
transforms:
  - class: QCFilterTransform
    kwargs:
      bounds: 'S330SpeedKt:0.0:0.5'
      message: set_active_mode underway
```

`bounds` takes comma-separated `field:low:high` triplets describing
the *normal* range; the message is emitted when a value falls outside
it. The transform fires in one direction only, so switching back when
the ship slows again takes a second logger (or a `ComposedWriter`)
with the complementary bounds. And since the condition is just a
transform, a
[`ComputedFieldsTransform`]({{ "/guide/computed-values/#computed-fields" | relative_url }})
rule that evaluates to a command string — or to `None` — can express
whatever logic the ship's operating rules require, with the
`LoggerManagerWriter` unchanged downstream.
