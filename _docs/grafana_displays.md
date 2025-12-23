---
permalink: /grafana_displays/
title: "Grafana/InfluxDB-based Displays"
layout: single
toc: true
toc_label: "Contents"
toc_icon: "list"
toc_sticky: true  # Makes the TOC stick on scroll
---
InfluxDB is a widely-used open source time series database. Grafana is
an open source visualization package. Used together, the two allow
drag-and-drop creation of sophisticated data displays that meet and
exceed the power of OpenRVDAS display tools. We strongly encourage
OpenRVDAS users to focus their efforts toward creating data displays
on the use of Grafana and InfluxDB. Telegraf is an additional package
that can collect system variables such as disk and memory usage and
feed them to InfluxDB.

In the past, OpenRVDAS supported a script, `utils/install_influxdb.sh`, now deprecated, that attempted to automate installation of these systems. Constant changes to InfluxDB and Grafana versions have made that a somewhat fraught and time-consuming project. We now recommend that users refer directly to the latest installation instructions for the packages in question.

This document provides guidance on how to find those instructions, and how to configure OpenRVDAS to work with the installed packages.

---
## InfluxDB

The latest package can be retrieved at
<https://www.influxdata.com/products/influxdb/>; follow the installation guide appropriate for your platform (Linux, macOS, Windows, Docker, or cloud) and verify that the InfluxDB service is running before continuing.

### Initial setup

Once InfluxDB is installed and running, you must create an authentication token that external applications can use to write data.

If this is a new installation, complete the initial setup process (via the web UI or CLI) to create:
- An organization (typically `openrvdas`)
- A bucket (again, typically `openrvdas`)
- An initial admin user (typically the user defined in the OpenRVDAS installation)

During this setup, InfluxDB will generate one or more authentication tokens.

### Create a token (if one does not already exist)

If you need to create a new token:
1. Open the InfluxDB user interface (typically at <http://localhost:8086>)
2. Log in as an admin user
3. Navigate to Load Data → API Tokens (or Settings → Tokens, depending on version)
4. Create a new token with the appropriate permissions. E.g. with write access to the target bucket
5. Save the generated token somewhere secure. Tokens are shown only once, when generated; if you lose yours, you will need to generate a new one when you want to give some other system, such as OpenRVDAS or Grafana, access to InfluxDB.

### Configure OpenRVDAS to use your InfluxDB setup

The main way OpenRVDAS interacts with InfluxDB is via the [`InfluxDBWriter`](https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/influxdb_writer.py). To function properly you can either pass it the organization, bucket name and authentication token you created above during instantiation, e.g.

```
  writer = InfluxDBWriter(org='openrvdas', bucket_name='openrvdas',
                          auth_token='8oyxASrMAqb6EzVfxSBvh....',
                          url='http://localhost:8086')
```
or you can copy that information into a settings file and have it read automatically.

To have values read automatically, copy `database/influxdb/settings.py` over into `database/influxdb/settings.py` and edit the default values to match your setup:
```
# InfluxDB settings
INFLUXDB_URL = 'http://localhost:8086'
INFLUXDB_ORG = 'openrvdas'
INFLUXDB_BUCKET = 'openrvdas'
INFLUXDB_AUTH_TOKEN = '8oyxASrMAqb6EzVfxSBvh1iI...'
```

---
## Grafana

Grafana is an open source visualization and dashboarding system that can read data from a wide variety of sources, including InfluxDB. When used together, Grafana provides a powerful, flexible, and actively maintained replacement for legacy OpenRVDAS display tools.

### Installation

Grafana installation procedures vary by operating system and deployment method.  
Please install Grafana by following the official instructions provided by Grafana Labs: <https://grafana.com/grafana/download>.

Choose the installation method appropriate for your platform (Linux packages, macOS, Windows, Docker, or cloud) and verify that the Grafana service is running before continuing.

Once installed, the Grafana web interface is typically available at <http://localhost:3000>.

Log in using the credentials created during installation (or the default credentials, if applicable), and complete any initial setup steps required by your installation.

---

### Configure Grafana to Access InfluxDB

After Grafana is running, you must configure it with a **data source** pointing to your InfluxDB instance.

1. Open the Grafana web interface.
2. Navigate to **Configuration → Data sources** (or **Connections → Data sources**, depending on version).
3. Click **Add data source**.
4. Select **InfluxDB** from the list of available data sources.

You will then be prompted to enter connection details for your InfluxDB installation.

Typical settings include:

- **Query language**: Flux (for InfluxDB 2.x and later)
- **URL**: <http://localhost:8086>
- **Organization**: openrvdas (or as you specified in InfluxDB)
- **Bucket**: openrvdas (or as you specified in InfluxDB)
- **Authentication**: Use an API token
- **Token**: Paste the InfluxDB authentication token created during the InfluxDB setup

After entering these values, click **Save & Test** to verify that Grafana can connect to InfluxDB.

---

### Notes on Authentication Tokens

Grafana uses the same InfluxDB API tokens described in the InfluxDB section above. The token must have at least **read access** to the bucket being visualized.

As with all API tokens:
- Store them securely
- Do not commit them to version control
- Limit permissions to the minimum required

---
### Sample Flux Query

The following is a simple example of a Flux query that can be used in Grafana to retrieve recent OpenRVDAS data from InfluxDB:

```flux
from(bucket: "openrvdas")
|> range(start: -15m)
|> filter(fn: (r) => r._measurement == "s330")
|> filter(fn: (r) => r._field == "S330HeadingTrue")
|> aggregateWindow(every: 10s, fn: mean, createEmpty: false)
|> yield(name: "mean")
```
This query:
* Reads data from the openrvdas bucket
* Selects data from the last 15 minutes
* Filters on a specific measurement and field
* Aggregates values into 10-second averages

You can adapt the measurement name, fields, time range, and aggregation function to suit your OpenRVDAS configuration and display requirements.

### Creating Dashboards

Once the InfluxDB data source is configured, Grafana can be used to create dashboards and panels that visualize OpenRVDAS data stored in InfluxDB. Dashboards can be created interactively using Grafana’s web interface and shared or exported as needed.

Refer to the Grafana documentation for details on dashboard creation, panel types, and query syntax.

---
### Grafana Plugins and Dashboards

Grafana ships with a comprehensive set of built-in plugins that are sufficient for most OpenRVDAS visualization needs. In general, **no additional Grafana plugins are required** to work with OpenRVDAS and InfluxDB.

#### Built-in Plugins

The standard Grafana installation includes core panel types and data sources such as:

- Time series
- Table
- Stat
- Gauge / Bar gauge
- Heatmap
- State timeline
- Text
- InfluxDB data source

These built-in plugins are actively maintained as part of Grafana and require no separate installation.

---

#### Optional Plugins

In some cases, additional plugins may be useful, though they are not required. Examples include:

- **Geomap panel**  -  Useful for displaying position or track data (latitude/longitude) stored in InfluxDB.

- **Plotly panel**  -  Allows advanced plotting and interactive visualizations.

- **Discrete panel (legacy)** -  Useful for categorical or state-based data (note that newer Grafana versions provide built-in alternatives such as State timeline).

Optional plugins can be installed using Grafana’s plugin manager or command-line tools. Refer to the Grafana documentation for plugin installation instructions.


One particularly useful panel that can be added is the [Ocean Data Tools Compass Panel](https://github.com/OceanDataTools/grafana-compass-panel). Please visit <https://github.com/OceanDataTools/grafana-compass-panel> for instructions how to install and configure it for your system.

![Grafana Compass Panel](../assets/images/grafana_compass_panel.png)

> Note: Plugin availability and compatibility may vary between Grafana versions.

---
### Importing and Exporting Dashboards

Grafana dashboards can be easily shared and reused.

#### Exporting a dashboard

1. Open the dashboard in Grafana.
2. Click **Dashboard settings → JSON model**.
3. Copy or download the dashboard JSON.

This JSON file can be stored in version control or shared with other users.

#### Importing a dashboard

1. Navigate to **Dashboards → Import**.
2. Paste the dashboard JSON or upload the JSON file.
3. Select the appropriate InfluxDB data source when prompted.
4. Complete the import.

This allows dashboards to be reused across systems with minimal changes.

Several pre-built dashboards that can be adapted to use by other installations are available in the [OpenRVDAS sample USAP installation directory](https://github.com/OceanDataTools/openrvdas_usap/tree/main/nbp/dashboards).

---

### Notes

- Dashboards created for OpenRVDAS typically rely only on standard Grafana panels and the InfluxDB data source.
- When importing dashboards, ensure that measurement names, fields, and bucket names match your InfluxDB configuration.
- Grafana plugins and dashboards are independent of OpenRVDAS and can be added or removed without affecting data collection.

---
## Telegraf (Optional)

Telegraf is an open source agent for collecting system and application metrics and writing them to time series databases such as InfluxDB. When used with OpenRVDAS, Telegraf can be configured to collect system-level metrics (for example CPU usage, memory usage, disk activity, and network statistics) and store them alongside OpenRVDAS data in InfluxDB for visualization in Grafana.

---
### Installation

Telegraf installation procedures vary by operating system and deployment method.  
Please install Telegraf by following the official instructions provided by InfluxData: <https://www.influxdata.com/time-series-platform/telegraf/>.

Choose the installation method appropriate for your platform (Linux packages, macOS, Windows, Docker, or cloud) and verify that the Telegraf service is installed before continuing.

---

### Configure Telegraf to Write to InfluxDB

Once Telegraf is installed, it must be configured to write collected metrics to your InfluxDB instance.

Telegraf configuration is typically stored in a file named `telegraf.conf` (the exact location depends on your platform). Edit this file and configure the InfluxDB output plugin to match your InfluxDB setup.

For InfluxDB 2.x and later, configure the `influxdb_v2` output plugin. A minimal example is shown below:

```toml
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "8oyxASrMAqb6EzVfxSBvh1iI..."
  organization = "openrvdas"
  bucket = "system_health"
 ```

The authentication token must have write access to the specified bucket.

---
### Enable Input Plugins
Telegraf collects data through input plugins. Common system-level input plugins include:
* cpu
* mem 
* disk 
* diskio 
* net 
* system

These are often enabled by default. You may adjust their settings in telegraf.conf as needed for your environment. For example:
```toml
[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
  report_active = true

[[inputs.mem]]

[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs"]

[[inputs.net]]
```
Refer to the Telegraf documentation for a full list of available plugins and configuration options.

---
### Start and Verify Telegraf
After configuring Telegraf, start (or restart) the Telegraf service according to your platform’s conventions (for example, using systemctl, service, or a container runtime).

Once running, verify that:
* Telegraf is active and not reporting errors 
* Metrics are appearing in the specified InfluxDB bucket

You can confirm data ingestion by:
* Viewing logs from the Telegraf service 
* Using the InfluxDB web UI to browse recent data
* Querying the data from Grafana

---
### Notes
* Telegraf is optional and not required for OpenRVDAS operation. 
* Telegraf metrics can be visualized in Grafana using the same InfluxDB data source configured earlier. 
* As with all authentication tokens, store the InfluxDB token securely and limit permissions to only what is required.

---
## Managing InfluxDB, Grafana, and Telegraf Services

InfluxDB, Grafana, and Telegraf are long-running services and must be managed so that they start automatically, restart on failure, and shut down cleanly. How this is done depends on how the software was installed and the conventions of your operating system.

Common approaches include:

- Native service managers (e.g. `systemd` on Linux, `launchd` on macOS)
- Container orchestration (e.g. Docker, Docker Compose)
- Process supervisors such as `supervisord`

Any of these approaches are valid, provided the services are kept running reliably.

---

### Example: Managing Services with Supervisor

One way to manage InfluxDB, Grafana, and Telegraf is to use **Supervisor**, in the same way OpenRVDAS services are often managed.

When using Supervisor, a configuration file can be created in the appropriate directory (for example, `/etc/supervisor/conf.d/`) that defines how each service should be started and monitored.

The following example parallels the `openrvdas.conf` files typically found in the same directory and reflects the configuration generated by the legacy `utils/install_influxdb.sh` script:

```ini
; Control file for InfluxDB, Grafana and Telegraf. Generated using the
; openrvdas/utils/install_influxdb.sh script

; Run InfluxDB
[program:influxdb]
command=/usr/bin/influxd --reporting-disabled
directory=/opt/openrvdas
;environment=INFLUXD_CONFIG_PATH=/etc/influxdb
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/openrvdas/influxdb.stderr
user=rvdas

; Run Grafana
[program:grafana]
command=/usr/sbin/grafana-server --homepath /usr/share/grafana
directory=/usr/share/grafana
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/openrvdas/grafana.stderr
;user=rvdas

; Run Telegraf
[program:telegraf]
command=/usr/bin/telegraf --config=/etc/telegraf/telegraf.d/openrvdas.conf
directory=/opt/openrvdas
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/openrvdas/telegraf.stderr
user=rvdas

[group:influx]
programs=influxdb,grafana,telegraf
```
