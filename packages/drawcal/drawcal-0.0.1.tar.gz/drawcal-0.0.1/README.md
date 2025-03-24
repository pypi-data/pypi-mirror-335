drawcal
=======

Python library for drawing simple monthly calendar images with events.

## Installation

The easiest way to install:

```bash
$ pip install -U drawcal
```

## Quickstart

Generate a calendar image for a given events file:

```bash
$ drawcal --events events.json --month 3 --year 2025
```

Python:

```python
>>> from drawcal import draw_calendar
>>> draw_calendar(month, year, events=events, outfile=outfile)
```
