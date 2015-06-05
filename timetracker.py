#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##    Copyright 2015 Rasmus Scholer Sorensen, rasmusscholer@gmail.com
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##

# pylint: disable=C0103

"""

Read and write TimeTracker files in simple line-by-line format.

The format is:
    %DATE %TIME [start/stop] [activity]


"""

import os
from datetime import datetime
import logging
logger = logging.getLogger(__file__)


## Sublime imports:
import sublime
import sublime_plugin

## Constants
SETTINGS_NAME = "TimeTracker.sublime-settings"



def get_settings():
    """ Get TimeTracker settings. """
    return sublime.load_settings(SETTINGS_NAME)

def get_setting(key, setting=None, settings=None):
    """
    Specify the settings will basically just do settings.get(key)
    """
    if settings is None:
        settings = sublime.load_settings(SETTINGS_NAME)
    return settings.get(key)

def persist_setting(key, value):
    """ Persist a settings key and value in TimeTracker settings. """
    settings = sublime.load_settings(SETTINGS_NAME)
    settings.set(key, value)
    sublime.save_settings(SETTINGS_NAME)

def append_line(line, filename=None, add_newline=True):
    """
    Append <line> to <filename>, adding newline unless disabled.
    If filename is not given, will use timetracker_filename value from TimeTracker settings file.
    """
    if filename is None:
        filename = os.path.expanduser(get_setting("timetracker_filename"))
    if add_newline:
        line += "\n"
    with open(filename, 'a') as fp:
        nchars = fp.write(line)
    logger.info("%s chars written to file %s", nchars, filename)
    return nchars, filename

def add_trackcmd(trackcmd, timestamp=None, filename=None):
    """
    trackcmd is just (start/stop) + activity
    """
    if timestamp is None:
        timefmt = get_setting("timetracker_datetimefmt", "%Y-%m-%d %H.%M")
        timestamp = datetime.now().strftime(timefmt)
    line = " ".join([timestamp, trackcmd])
    return append_line(line, filename, add_newline=True)

def start_activity(activity):
    trackcmd = "start " + activity.strip()
    return add_trackcmd(trackcmd)

def stop_activity(activity):
    trackcmd = "stop " + activity.strip()
    return add_trackcmd(trackcmd)



class TimetrackerAddTrackcmd(sublime_plugin.WindowCommand):
    """
    Set AutoRemote key.
    Command string: timetracker_add_trackcmd (WindowCommand)
    """
    def run(self, trackcmd=None):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        self.window.show_input_panel('Track cmd:', trackcmd or '', self.on_done, None, None)

    def on_done(self, trackcmd):
        if not trackcmd:
            msg = "Track cmd is empty."
        else:
            nchars, filename = add_trackcmd(trackcmd)
            try:
                msg = "%s chars written to file %s" % (nchars, filename)
            except (FileNotFoundError, IOError) as e:
                msg = "Failed to append entry to file. %s: %s" % (type(e), e)
        print(msg)
        sublime.status_message(msg)


class TimetrackerStartActivity(sublime_plugin.WindowCommand):
    """
    Set AutoRemote key.
    Command string: timetracker_start_activity (WindowCommand)
    """
    def run(self, activity=None):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        self.window.show_input_panel('Start activity:', activity or '', self.on_done, None, None)

    def on_done(self, activity):
        if not activity:
            msg = "Activity is empty."
        else:
            nchars, filename = start_activity(activity)
            try:
                msg = "%s chars written to file %s" % (nchars, filename)
            except (FileNotFoundError, IOError) as e:
                msg = "Failed to append entry to file. %s: %s" % (type(e), e)
        print(msg)
        sublime.status_message(msg)


class TimetrackerStopActivity(sublime_plugin.WindowCommand):
    """
    Set AutoRemote key.
    Command string: timetracker_stop_activity (WindowCommand)
    """
    def run(self, activity=None):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        self.window.show_input_panel('Stop activity:', activity or '', self.on_done, None, None)

    def on_done(self, activity):
        if not activity:
            msg = "Activity is empty."
        else:
            nchars, filename = stop_activity(activity)
            try:
                msg = "%s chars written to file %s" % (nchars, filename)
            except (FileNotFoundError, IOError) as e:
                msg = "Failed to append entry to file. %s: %s" % (type(e), e)
        print(msg)
        sublime.status_message(msg)


class TimetrackerOpenLog(sublime_plugin.WindowCommand):
    """
    Set AutoRemote key.
    Command string: timetracker_open_log (WindowCommand)
    """
    def run(self, activity=None):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        filename = get_setting("timetracker_filename")
        #print(filename)
        #self.window.run_command('open_file', {"file": filename})
        # doesn't work, sublime don't recognize absolute windows paths.
        self.window.open_file(filename)
