json-summarizer
===============

Summarizes JSON file contents (or native Python data structures)

Pretty easy to run in Python 2.X (tested on Python 2.7):

    python summarize_json.py <JSON file>

This script prints out a summary of your JSON file's contents, essentially inferring a schema using some simple heuristics.

It comes in handy for understanding the structure of a blob of JSON (or native Python) data that someone else hands to you
without proper documentation. And it can also be used to manually sanity-check files for
outliers, weird values, inconsistencies, etc.

Project instigated by [this Twitter conversation](https://twitter.com/edwardbenson/status/357932092841144321) on 2013-07-18.

Email philip@pgbovine.net with bug reports, feature requests, etc.
