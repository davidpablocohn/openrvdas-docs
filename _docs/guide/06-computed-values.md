---
permalink: /guide/computed-values/
title: "Computed and Calibrated Values"
layout: single
toc: true
toc_label: "In this section"
toc_icon: "list"
toc_sticky: true
---
Raw sensor output is rarely the number science wants. This section covers
turning measured values into derived ones — true winds from relative,
calibrated temperatures from raw counts — and keeping the calibration
coefficients behind them honest.

# Computed Fields

*Not yet rewritten. In the meantime, see
[Computed Fields]({{ "/computed_fields/" | relative_url }}).*

Declaring derived values alongside the fields they're computed from (new
in v2.7.0), and when to use a computed field versus a derived-data logger.

# Calibrations

*Not yet rewritten. In the meantime, see
[Calibrated Values]({{ "/cookbook/calibrated_values/" | relative_url }}).*

Applying calibration coefficients to raw values — and the hygiene around
them: where coefficients come from, keeping them with your institution's
configuration under version control, and recording which coefficients
were in effect when (see
[Snapshots and the State Journal]({{ "/guide/operations/#snapshots-and-the-state-journal" | relative_url }})).

# Averaging and Resampling

*Not yet rewritten. In the meantime, see
[Averaging and Resampling]({{ "/interpolation_transform/" | relative_url }}).*

The InterpolationTransform: smoothing noisy fields, resampling to fixed
intervals, and feeding the results back as new named fields.

# Derived Data Loggers

*Not yet rewritten. In the meantime, see
[Derived Data Loggers]({{ "/derived_data/" | relative_url }}).*

The loop-through-the-cached-data-server pattern: a logger that subscribes
to fields other loggers produce, computes new values (true winds being
the classic case), and publishes them back for displays and storage.
