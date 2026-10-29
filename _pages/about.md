---
permalink: /about/
title: "About"
layout: single
toc: true
toc_label: "Contents"
toc_icon: "list"
toc_sticky: true  # Makes the TOC stick on scroll
---
OpenRVDAS, the Open Research Vessel Data Acquisition System, is a
software framework for building data acquisition systems. It is written
for the operators of oceanographic research vessels, and for anyone
else who runs a platform full of instruments and needs to record what
they say. OpenRVDAS reads data records from serial ports and from
network-connected sensors, optionally changes them on the way through
(adding timestamps, parsing them into named fields, computing derived
values) and streams the results to wherever they need to go: logfiles,
network ports, databases, and live displays.

Rather than a finished application, OpenRVDAS is a kit of small
components, Readers, Transforms and Writers, with one simple interface
in common, which you snap together into the system your vessel needs.

## Design Philosophy

Every ship has different requirements, and those requirements change
from mission to mission and from year to year. No single turnkey system
can serve everyone, and no fixed system stays right for long.

So OpenRVDAS doesn't try to be one. It is an architecture for
assembling small, modular pieces into whatever is needed in a given
situation, and for changing that assembly when the situation changes.
A data pipeline is a few lines of YAML naming its components; a new
instrument is a new pipeline; a new kind of instrument is a new
component, written in a few dozen lines of Python against the same
interface as the standard ones. The system you end up with matches your
vessel exactly, because you described it.

## Origins

OpenRVDAS was begun in 2017, written from a clean slate on the basis of
experience developing data acquisition code for the United States
Antarctic Program and its Antarctic Support Contract. Its design has
been heavily informed by discussion and collaboration with members of
the [RVTEC community](https://www.unols.org/committee/research-vessel-technical-enhancement-committee-rvtec),
the technical staff of the US academic research fleet. It is in
production use on research vessels around the world and under active
development.

OpenRVDAS is part of the [Ocean Data Tools](https://oceandata.tools)
project, alongside Sealog, the shipboard event logger it works with.

## Requirements and License

OpenRVDAS runs on Linux (Ubuntu, Debian and Raspbian; CentOS, RHEL,
Rocky and AlmaLinux) and macOS, and needs Python 3.8 or newer. Its web
console works in any modern browser. The details, and what the
installer will ask you, are in the Guide's
[Installation]({{ "/guide/installation/" | relative_url }}) section.

The code is at
[github.com/OceanDataTools/openrvdas](https://github.com/OceanDataTools/openrvdas),
under the [MIT License](https://opensource.org/license/mit). Bug
reports and pull requests are welcome there.

## Where to Start

The [OpenRVDAS Guide]({{ "/guide/introduction/" | relative_url }}) is
the manual: one document, front to back, from what OpenRVDAS is to how
to fix it when it misbehaves. Its introduction has a
[reading guide]({{ "/guide/introduction/#how-to-read-this-guide" | relative_url }})
that points you to the right section for your situation, whether you're
standing watch on a vessel that already runs OpenRVDAS, installing it
on a new machine, or bringing it up on your own vessel. If you'd rather
see it working first, the
[tutorial]({{ "/guide/nbp-tutorial/" | relative_url }}) runs a complete
simulated vessel on your own machine.
