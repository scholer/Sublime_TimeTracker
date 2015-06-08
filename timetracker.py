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

# pylint: disable=C0103,W0201,W0221,R0201

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

def get_setting(key, default=None, settings=None):
    """
    Specify the settings will basically just do settings.get(key)
    """
    if settings is None:
        settings = sublime.load_settings(SETTINGS_NAME)
    return settings.get(key, default)

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
    """ Shortcut to add a "start <activity>" entry. """
    trackcmd = "start " + activity.strip()
    recently_started = get_setting("timetracker_recently_started", [])
    recently_started.append(activity.strip())
    persist_setting("timetracker_recently_started", recently_started)
    return add_trackcmd(trackcmd)

def stop_activity(activity):
    """ Shortcut to add a "stop <activity>" entry. """
    if activity == -1:
        recently_started = get_setting("timetracker_recently_started", [])
        activity = recently_started[-1]
    recently_stopped = get_setting("timetracker_recently_stopped", [])
    recently_stopped.append(activity.strip())
    persist_setting("timetracker_recently_stopped", recently_stopped)
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
        """ Receives input trackcmd as str. """
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
        if activity is None:
            recently_started = get_setting("timetracker_recently_started", [])
            recently_started = [item.split(",")[0].strip() for item in recently_started]
            try:
                activity = recently_started[-1]
            except ValueError:
                pass
        self.window.show_input_panel('Start activity:', activity or '', self.on_done, None, None)

    def on_done(self, activity):
        """ Receives input activity (label) as str. """
        if not activity:
            msg = "Activity is empty."
        else:
            try:
                nchars, filename = start_activity(activity)
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
        if activity is None:
            recently_started = get_setting("timetracker_recently_started", [])
            recently_started = [item.split(",")[0].split("#")[0].strip() for item in recently_started]
            try:
                activity = recently_started[-1]
            except ValueError:
                pass
        self.window.show_input_panel('Stop activity:', activity or '', self.on_done, None, None)

    def on_done(self, activity):
        """ Receives input activity (label) as str. """
        if not activity:
            msg = "Activity is empty."
        else:
            try:
                nchars, filename = stop_activity(activity)
                msg = "%s chars written to file %s" % (nchars, filename)
            except (FileNotFoundError, IOError) as e:
                msg = "Failed to append entry to file. %s: %s" % (type(e), e)
        print(msg)
        sublime.status_message(msg)


class TimetrackerStartActivityQuickpanel(sublime_plugin.WindowCommand):
    """
    Set AutoRemote key.
    Command string: timetracker_start_activity_quickpanel (WindowCommand)
    """
    def run(self, activity=None):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        recently_started = get_setting("timetracker_recently_started", [])
        if not recently_started:
            msg = "List of recently started activities is empty; Use manual input first."
            print(msg)
            sublime.status_message(msg)
            return
        if activity is None or activity == -1:
            activity = recently_started[-1]
        recent_cleaned = [item.split(",")[0].split("#")[0].strip() for item in recently_started]
        self.activities = sorted(set(recent_cleaned))
        selected_index = self.activities.index(recent_cleaned[-1])
        self.window.show_quick_panel(self.activities, self.on_selected, selected_index=selected_index)

    def on_selected(self, index):
        """ Receives input activity (label) as str. """
        if index == -1:
            print("Quick panel cancelled")
            return
        self.activity = self.activities[index]
        self.window.show_input_panel('Comment:', '', self.on_done, None, None)

    def on_done(self, comment):
        """ Write activity + comment. """
        if comment:
            self.activity = self.activity + ", " + comment
        try:
            nchars, filename = start_activity(self.activity)
            msg = "%s chars written to file %s" % (nchars, filename)
        except (FileNotFoundError, IOError) as e:
            msg = "Failed to append entry to file. %s: %s" % (type(e), e)
        print(msg)
        sublime.status_message(msg)



class TimetrackerStopActivityQuickpanel(TimetrackerStartActivityQuickpanel):
    """
    Set AutoRemote key.
    Command string: timetracker_stop_activity_quickpanel (WindowCommand)
    Inherits from TimetrackerStartActivityQuickpanel
    """
    def on_selected(self, index):
        """ Receives input activity (label) as str. """
        if index == -1:
            print("Quick panel cancelled")
            return
        activity = self.activities[index]
        try:
            nchars, filename = stop_activity(activity)
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
    def run(self, logname=None):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        if logname is None:
            filename = get_setting("timetracker_filename")
        else:
            filename = get_setting("timetracker_all_logs").get(logname)
        #self.window.run_command('open_file', {"file": filename})
        # doesn't work, sublime don't recognize absolute windows paths.
        self.window.open_file(filename)


class TimetrackerSelectOpenLog(sublime_plugin.WindowCommand):
    """
    Set AutoRemote key.
    Command string: timetracker_select_open_log (WindowCommand)
    """
    def run(self):
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        #if logname is None:
        #    filename = get_setting("timetracker_filename")
        #else:
        #    filename = get_setting("timetracker_all_logs").get(logname)
        self.logs = get_setting("timetracker_all_logs")
        self.lognames = sorted(self.logs.keys())
        self.window.show_quick_panel(self.lognames, self.on_done)

    def on_done(self, index):
        """ Receives selected index for lognames list. """
        #print(filename)
        #self.window.run_command('open_file', {"file": filename})
        # doesn't work, sublime don't recognize absolute windows paths.
        if index == -1:
            print("Quick panel cancelled")
            return
        filename = self.logs[self.lognames[index]]
        self.window.open_file(filename)
