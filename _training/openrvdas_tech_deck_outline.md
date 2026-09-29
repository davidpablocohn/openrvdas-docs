# Keeping OpenRVDAS Running: slide outline (60 min)

Working outline for tuning the story. There is one line per slide, and each
slide has a point to land. Minutes are for the whole section and include
demos and drills. `→` shows where a slide came from in `openrvdas_tech_deck.md`.

The session is 45 min on core OpenRVDAS plus a 15 min wraparound. The
wraparound covers where CORIOLIX sits, and what InfluxDB and Grafana do with
OpenRVDAS output. The CORIOLIX team's one-hour talk follows, so this session
sets expectations for it and doesn't try to cover CORIOLIX itself.

**Commands:** the deck uses the short installed commands throughout: `listen`,
`validate_config`, `simulate_data`. Slide 8 carries the one-line note on where
they come from and what to fall back to.

**Two kinds of "log":** the deck keeps these apart every time they come up.
- *Data files* are what a `LogfileWriter` produces: the archive. They're
  checked with `tail -f`.
- *stderr files* are a process's error output: diagnostics. They're read
  with `less` or in the console.

**The thread through the whole talk:** *which side of the line am I on?*
OpenRVDAS gets data off the instruments and hands it to its writers: files,
the network, and databases. InfluxDB stores what an `InfluxDBWriter` sends it,
and Grafana draws and QCs what InfluxDB holds. On CORIOLIX (CX) ships, a
`CORIOLIXWriter` also writes to whatever database backend CX is installed
with, and CX sits on top of OpenRVDAS. Slide 3 draws the picture, §7 explains the InfluxDB/Grafana half,
and slide 30 turns it into a troubleshooting question.

Target: 35 slides in 60 min.

---

## 1. Why you are here (5 min)

1. **Title**: "Working Onboard with OpenRVDAS"
2. **What you'll be able to do**: understand the organization, read the
   console, read configs, troubleshoot, **and tell whether a problem is in
   OpenRVDAS or downstream of it**. Installing and writing loggers are a bonus.
3. **Where OpenRVDAS sits** (diagram, ref):
   - instruments → **OpenRVDAS**
   - OpenRVDAS processes the data and writes it to **files, the network, and databases** such as
     **InfluxDB**. On CX ships it also writes to **CX's database backend**,
     using `CORIOLIXWriter`.
   - **Grafana** reads from InfluxDB (or other suitable database) to produce dashboards
   - **CORIOLIX** reads from its own backend, and also wraps around OpenRVDAS
     itself (next slide)

   *Point: this hour is the OpenRVDAS layer and the handoff to the layers above.
   Every later "which side is it?" question points back to this picture.*
4. **OpenRVDAS and CORIOLIX**: some ships run CORIOLIX (CX for short), a system that sits on
   top of OpenRVDAS. Among other things, it:
   - keeps OpenRVDAS running
   - manages its configurations
   - processes and routes its output to create off-ship "datapresence"

   OpenRVDAS hands data to CX through a `CORIOLIXWriter`, which writes to
   whatever database backend CX is installed with. The following hour
   will cover CORIOLIX in depth, so save CORIOLIX questions for the CORIOLIX team.
   *Point: on a CORIOLIX ship, some of what this talk does by hand (loading
   configs, changing modes) may be done through CORIOLIX instead. The
   OpenRVDAS pieces underneath (loggers, stderr, `listen`) are the same.*
   - *To confirm with the CORIOLIX presenters: how they describe the
     relationship. The slide should use their words, so the two talks agree.*
5. **The whole system in one sentence**: read → transform → write, snapped
   together by a config file. *Point: every OpenRVDAS screen today is a view
   of this.*

## 2. Readers, transforms, writers (8 min)

6. **Three components**: one line each, with 2–3 example classes apiece.
   Writers include `InfluxDBWriter`, planted here for §7
   → merges "Three basic components" with the separate Readers, Transforms
   and Writers slides.
7. **Snapping them together**: readers in parallel, transforms in series,
   writers in parallel (diagram). *Point: transform order matters; one record
   can go to several writers.*
8. **Demo: from flags to a file**: one continuous demo.
   1. `listen --serial port=/tmp/tty_s330`. With no writer given, output goes
      to the screen.
   2. Add a timestamp, a prefix, a file writer and a UDP writer.
   3. Run the same logger from a file with `listen s330.yaml`. Show that the
      file says what the flags said.

   *Point: `listen` is the single most useful tool, and a config file is just
   flags written down. The next section teaches how to read that file.*
   - Small-print note: `listen` is a shortcut for `logger/listener/listen.py`
     (the same goes for `validate_config` and `simulate_data`). The installer
     adds these to the OpenRVDAS venv, so run
     `source /opt/openrvdas/venv/bin/activate` first. If a command isn't found
     (the venv isn't active, or the install predates the change), run the
     script by path from `/opt/openrvdas` instead. The arguments are the same.

   → absorbs "Our first logger" and "From command line to config file".

## 3. Enough YAML to be dangerous (5 min)

9. **Configs are files, written in YAML**: key-value pairs and lists, shown
   on the `s330.yaml` from the demo, which the room has just watched run
   → merges "Why configurations are files" with "YAML is two things".
10. **Indentation is structure** (gotcha): the same `s330.yaml`, showing how
    indentation carries its structure. Spaces only, and a setting under the
    wrong parent fails silently.
11. **Validate, don't guess** (demo): `validate_config`. Put a tab in
    `s330.yaml` and show the error.
    - "Values that bite" moves to §5 (slide 20), where its examples live.

## 4. Defining one logger (6 min)

12. **The anatomy of a logger config**: three keys (readers / transforms /
    writers) in dataflow order. Point back at `s330.yaml` from the demo.
13. **class + kwargs**: the one pattern, with the API reference as the source
    of truth.
14. **A real config, line by line**: read `knud-net` aloud, with `readers` and
    `writers` written as lists
    → replaces "In practice" and "A real configuration".
15. **One instrument, several configs**: `-off` / `-net` / `-net+file`.
    `off` is a real, empty config.
16. **Drill: read a config like a troubleshooter** (2 min): what does it
    depend on, and which destination goes quiet first?

## 5. Defining a whole cruise (6 min)

17. **The cruise definition**: one file for the whole ship, with its five
    top-level keys (ref).
18. **loggers and configs**: a "logger" is just a named group of configs; the
    running process is the config.
    - *Plant for §8:* any one config runs straight from the cruise file with
      `listen cruise.yaml:knud-net`.
19. **Modes: the operational switch**: port / underway, and one change puts
    the whole ship in a known state.
20. **Values that bite** (gotcha): why the `'off'` mode on the last slide is
    quoted, why the `cruise:` start and end dates on slide 17 need quotes,
    and the general rule for when to quote
    → moved here from §3, so it explains things the room has just seen.
21. **What a mode change actually does**: stop/start processes, one per
    config. *Point: this is what you're watching when a logger goes red.*
    - *(appendix: includes / variables / templates, "what you read isn't
      what runs")*

## 6. The servers that keep it running (7 min)

22. **The moving parts** (diagram): supervisord → logger_manager,
    cached_data_server, and the web stack. One-liner: "Displays blank but
    files growing = the cached data server, not the loggers."
    - If InfluxDB and Grafana are managed by supervisord on your ship, they
      appear in the same `status` listing. They're still separate systems,
      covered in §7.
23. **supervisord** (demo): `:9001` and `supervisorctl status`; restart the
    cached data server live.
24. **logger_manager**: runs the cruise, restarts failures. *Point:
    flickering means a restart loop, and that logger's stderr will say why.
    §8 shows where to find it.*
25. **Web console** (demo): modes, per-logger dropdown, stderr and the
    expanded config in one click.

## 7. Downstream: InfluxDB and Grafana (8 min)

This is new. It sits here because the room now knows what a writer is and
which servers OpenRVDAS runs. So "InfluxDB is fed by a writer" needs no new
concepts, and it comes just before troubleshooting, which relies on it.

26. **InfluxDB: a time-series store**: In many installations, OpenRVDAS writes to an external time series database with
    `InfluxDBWriter`, an ordinary writer at the end of an ordinary logger.
    Default bucket `openrvdas`; the measurement is the record's data_id;
    `:8086`, with a built-in Data Explorer.
    *Point: InfluxDB doesn't collect anything itself; it stores what a writer
    sends it.*
27. **Grafana: dashboards and QC**: it queries InfluxDB to draw panels, set
    thresholds and alerts, and run QC workflows. `:3000`.
    - Footnote: `GrafanaLiveWriter` can stream straight to a live Grafana
      panel with no database in between. Know which path your dashboards use.
28. **Demo: follow one field up the stack**: a field in `listen` output →
    the same field in the InfluxDB Data Explorer → the same field on a Grafana
    panel. *Point: each layer can be checked on its own. That becomes the
    §8 method.*
29. **Where OpenRVDAS stops, and where to get help** (ref):
    - The boundary is inside the `InfluxDBWriter`. If it can't connect or its
      token is rejected, the error shows up in *that OpenRVDAS logger's
      stderr*, even though the fix is on the InfluxDB side.
    - Anything after the data is stored (queries, panels, QC rules, alerts)
      belongs to Grafana.
    - The same rule applies on CX ships, where the boundary is inside the
      `CORIOLIXWriter`. That writer runs in an OpenRVDAS logger, so its
      errors are in that logger's stderr. Once the data is in CX's backend,
      it belongs to CX, which is the next talk.
    - Help, by layer:
      - OpenRVDAS docs: "Grafana/InfluxDB-based Displays" and "Grafana Live
        Setup"
      - InfluxData docs
      - Grafana docs and the Grafana community forum
      - CX: the CORIOLIX team (next talk)
      - Who owns the dashboards on your ship *(fill in per ship)*

## 8. Running it, and fixing it (12 min)

30. **OpenRVDAS or downstream?** Before you start debugging, work out which
    system you're in. Walk up the stack from slide 3:
    1. **Is OpenRVDAS producing it?** Is the logger green, and does data show
       up in `tail -f` or `listen --udp`? If not, it's OpenRVDAS, so go to
       slide 32.
    2. **Is it in InfluxDB?** Check the Data Explorer, set to the last 15 min.
       If not, read the `InfluxDBWriter` logger's stderr: connection, token,
       bucket.
    3. **Is the panel asking for it correctly?** Check the time range, bucket,
       field name and data source. If the data is in InfluxDB but not on the
       panel, it's a Grafana dashboard problem, not OpenRVDAS.
    - On a CX ship, the CX path works the same way as the InfluxDB path.
      OpenRVDAS is producing data but CX doesn't show it? Read the stderr of
      the logger with the `CORIOLIXWriter`. If it's clean, it's a CX
      question.
    - Small symptom table:
      - "Grafana says No data, but InfluxDB has it" → dashboard.
      - "InfluxDB empty, logger green, stderr shows 401" → token.
      - "Built-in displays blank, Grafana fine" → cached data server.
      - "CX missing data, `CORIOLIXWriter` logger green and stderr clean" →
        CX.
      - "Everything blank, including the data files" → OpenRVDAS, reader side.
31. **Follow the record**: a chain fails at one link; bisect, and don't
    reboot. Includes a one-line "what healthy looks like"
    → merges "Why this model makes debugging easy", "Healthy", and "The method".
32. **The triage ladder, OpenRVDAS side** (drill). It works from the outside
    in, and the least disruptive checks come first:
    1. **Console**: is the system in the mode you think? Is the logger in the
       config you expect? Is it green, red, or flickering?
    2. **Is data arriving where it should?**
       - A file writer means `tail -f` on the data file named in the config.
         Look for new lines, not just a file that exists.
       - A UDP writer means `listen --udp 6224`. Output goes to the screen,
         as in the first demo. Run it from another machine to test the
         network too.

       *If data is arriving, the logger is fine and the problem is
       downstream: back to slide 30.*
    3. **Read that logger's stderr**: in the console, or with
       `less /var/log/openrvdas/loggers/{logger}.stderr`. Start from the
       **first** error.
    4. **Stop the managed logger**, then run its config by hand:
       `listen cruise.yaml:knud-net -v`.
    5. **Still nothing? Read the port directly**. Silence and garbage
       characters point to different causes.
33. **Where the files are / take this with you** (ref): data files vs stderr
    files (per-logger and server); ports (`:80`, `:9001`, `:8766`, `:6224`,
    plus InfluxDB `:8086` and Grafana `:3000`); five commands; help sources by
    layer; what to send when you ask for help
    → merges "Where the log files are" with "Take this with you".
    - *(appendix / handout: the three "common failures" tables, plus a
      Grafana/InfluxDB table drawn from the docs' troubleshooting sections:
      InfluxDBWriter can't connect, Grafana "No data", token changed)*

Why this order: slide 30 sorts the problem into a system before slide 32 digs
into OpenRVDAS. Otherwise people spend twenty minutes on a healthy logger when
the problem is a Grafana time range. In the ladder, the data check (step 2)
comes before stderr. It takes seconds, changes nothing, and splits the problem
in half.

## 9. Handoff (2 min)

34. **What's next: CORIOLIX**: a one-slide recap of slide 3. OpenRVDAS gets
    data onto disk, the network and databases (including CX's backend,
    through `CORIOLIXWriter`), and CX builds on top.
    Suggest questions to bring to the next talk.
35. **Questions** (buffer, about 2 min)

---

## Decisions (applied in the rewrite)

- Triage order: console → data arriving? → stderr → stop and run by hand →
  port.
- The file-location reference moves out of §6 and merges with the takeaway
  slide at the end of §8.
- The drill in §4 is a slide of its own.
- YAML: indentation and the validator stay in §3, using `s330.yaml` as the
  example. "Values that bite" moves to §5, after Modes.
- The first demo is "flags to a file". Its first step uses no writer, so
  output goes to the screen. That's why the shorter `listen --udp 6224` later
  on needs no explanation.
- The short commands (`listen`, `validate_config`, `simulate_data`) are used
  everywhere, with the backup note on slide 8. `listen file.yaml` and
  `listen cruise.yaml:config` replace `--config_file`.
- The wraparound puts context up front (slides 3–4) and adds a downstream
  section (§7) before troubleshooting. "Which system is it?" is the first
  troubleshooting step (slide 30).

## Fixes to carry into the deck

- Title SAY: "the next hour", not "hour and a half".
- Objectives SAY: rewrite to match the bullets, which now include the
  OpenRVDAS-or-downstream skill.
- YAML section blurb: "Three slides".
- `knud-net`: `readers:` and `writers:` written as lists, matching `tsg1-net`.
- The old "Optional layers on top" slide is replaced by §7. Its "Grafana down
  ≠ data lost" line moves to slide 26 or 29.
- Every slide number, section blurb and "next slide" or "next section"
  reference in the SAY text gets updated for the new order. In particular,
  logger_manager now points forward to §8, not to "the next slide".
- Tag syntax (`{{demo}}` in the intro vs `{demo}` in headings): pick whichever
  one the HTML build expects. *To check during the rewrite.*
- The data-file path in step 2: use the `LogfileWriter` path from the demo
  config, so the room has already seen it. *To check against the sample
  cruise during the rewrite.*
- The InfluxDB and Grafana demo (slide 28) runs on a training machine with
  InfluxDB, Grafana and one `InfluxDBWriter` logger in the demo cruise.
  *Confirmed.*
- CX terms: the deck names the writer `CORIOLIXWriter`, and never ties CX
  to one particular database. It introduces "CX" on slide 4 and uses it
  from there on. *Confirmed.*
- Install questions for InfluxDB and Grafana point to the "Grafana/InfluxDB-based
  Displays" docs page and the vendors' instructions, not
  `utils/install_influxdb.sh`, which is deprecated. *Confirmed.*
