#! /usr/bin/env python3

#
# --------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2025 Martin Jan Köhler
# Johannes Kepler University, Institute for Integrated Circuits.
#
# This file is part of openpdk-pmap 
# (see https://github.com/martinjankoehler/openpdk-pmap).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# SPDX-License-Identifier: GPL-3.0-or-later
# --------------------------------------------------------------------------------
#
import psutil
import sys

def get_memory_usage(pid: int) -> int:
    process = psutil.Process(pid)
    mem = process.memory_info()
    mem_kb = mem.vms / 1024
    return mem_kb

def main():
    if len(sys.argv) != 2:
         print(f"Usage: {sys.argv[0]} <pid>")
         sys.exit(1)

    pid: int
    try:
        pid = int(sys.argv[1])
    except ValueError:
        print(f"ERROR: could not parse pid {sys.argv[1]}")
        sys.exit(2)

    mem_kb = get_memory_usage(pid)
    print(f" total           {round(mem_kb)}K")

if __name__ == '__main__':
    main()

