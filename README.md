Python S60 Projects
---

This repository is an archive of a variety of projects and general purpose libraries that I had created from 2011 to 2015.

They were created using the very handy [PED (Python EDitor) for S60](https://code.google.com/p/ped-s60/).
Yes, that does mean I made them solely on my phone, it was possible thanks to the
[Nokia SU-8W](https://www.phonearena.com/reviews/Nokia-Wireless-Keyboard-SU-8W-Review_id1860) bluetooth keyboard.


[PyS60](https://en.wikipedia.org/wiki/Python_for_S60) was my first introduction to Python, and more generally
to "platform development" (i.e. not web-based).

# Summary of projects

## 2048

A replica of the game [2048](https://en.wikipedia.org/wiki/2048_(video_game)).

This project is incomplete and does not implement all the rules of the game.

## Common Lib

These are the libraries that drive the projects

There is quite an extensive range of libraries. A lot of them revolve around extending the built-in GUI APIs.

## cURL Console

A console application that implements some of the features of [cURL](https://curl.haxx.se).

## Diff Tool

A tool that shows a [unified diff](https://en.wikipedia.org/wiki/Diff#Unified_format) of two files, with red/green/gray
colors to represent changed/same lines.

It uses the [`difflib`](https://docs.python.org/2/library/difflib.html) library to calculate the diff.

## File Manager / FTP Manager

Originally just as an FTP file explorer, but later became a general purpose file manager.

Features include:

- Browse both FTP and local file systems
- Edit Files. Supports syntax highlighters for HTML, PHP and JavaScript.  
  Text editor has support for auto-indent, find/replace, custom colors
- Delete files
- Create files
- Download files/directories
- Upload files, and extract local ZIP to remote directory
- View file metadata
- Clipboard to cut/copy/paste files
- Saved FTP settings as well as other application settings

## GitHub Mobile

Connects to the GitHub API and can download repositories.  
Can browse commits and allows local changes to be committed.

Has partial support for the git storage format.

## MHTML Reader

Reads MHTML files generated from OperaMobile.

## Other Lib

Some work-in-progress libraries and experiments.


## Planner

Keeps track of a class timetable and homework. Connects to the phone's calendar to manage events and deadlines.

## Playlist Generator

The first app I made. Generates m3u playlist files for the phone's [Music Player](https://www.gsmarena.com/sony_ericsson_satio_idou-review-358p4.php).

## Rubiks Cube

A work-in-progress Rubiks Cube game.

## Spykee

Controls a [Spykee](https://en.wikipedia.org/wiki/Spykee) by communicating to it over the LAN.

## Web Server

Uses a web server implementation I made for another project. Serves static files as well as parsing files for
`<?python` which executes on the server.
