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

Generate sublime command strings, etc.

"""

from string import ascii_uppercase

def command_classname_to_string(classname):
    return "".join("_"+c.lower() if c in ascii_uppercase else c for c in classname).strip("_")

def command_string_to_classname(cmdstring):
    return "".join(part.title() for part in cmdstring.split("_"))

def print_cmdstring(classname):
    print(command_classname_to_string(classname))

def print_cmdclass(cmdstring):
    print(command_string_to_classname(cmdstring))
