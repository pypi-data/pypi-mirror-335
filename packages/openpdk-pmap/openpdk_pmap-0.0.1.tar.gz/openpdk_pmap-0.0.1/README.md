<!--
--------------------------------------------------------------------------------
SPDX-FileCopyrightText: 2025 Martin Jan Köhler
Johannes Kepler University, Institute for Integrated Circuits.

This file is part of openpdk-pmap 
(see https://github.com/martinjankoehler/openpdk-pmap).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
SPDX-License-Identifier: GPL-3.0-or-later
--------------------------------------------------------------------------------
-->
[![PyPi](https://img.shields.io/pypi/v/openpdk-pmap)](https://pypi.org/project/openpdk-pmap/)
[![GitHub issues](https://img.shields.io/badge/issue_tracking-github-blue.svg)](https://github.com/martinjankoehler/openpdk-pmap/issues)

# pmap for OpenPDK LVS

LVS scripts KLayout in OpenPDKs like Skywater `sky130A` or IHP `sg13g2` observe the total memory usage using `pmap`, which exists on Linux, but not on macOS or Windows.

KLayout-PEX is a parasitic extraction tool for [KLayout](https://klayout.org), and uses this package as a dependency on these platforms.
Check out the [documentation website](https://martinjankoehler.github.io/klayout-pex-website) for more information.

## Dependencies

- `psutil`

## Install

`pip install openpdk-pmap`

After that, you should be able to run `pmap`.

## Acknowledgements

Special thanks to the public funded German project FMD-QNC (16ME0831)
https://www.elektronikforschung.de/projekte/fmd-qnc for financial
support to this work.
