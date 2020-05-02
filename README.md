### readynas-to-telegraf

Script to gather SNMP health and performance data from a Netgear ReadyNAS unit and pass it to the Telegraf exec plugin.  The information gathered is reformatted to make it more dashboard friendly.

### License

MIT License

Copyright (c) 2020 Ross A. Stewart

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Compatibility

The script has been tested on a ReadyNAS RN204 running firmware version 6.10.2

### Installation

#### Python Dependencies

- Python SNMP Utilities - https://github.com/rosskouk/python_snmp_utilities.git

#### Submodules

This project uses submodules and they need to be set up before the utility can be used.
After cloning the repository run the following commands:

```bash
git submodule init
git submodule update
```

#### Telegraf

Install the program as you would any other script that will be used by the **exec** plugin.
You must copy the READYNASOS-MIB on the system running Telegraf

Once the MIB is installed add a configuration file for the readynas-to-telegraf, example configuration is below.

##### Example Telegraf Configuration

```bash
[[inputs.exec]]
  commands = [ "/etc/telegraf/scripts/readynas-to-telegraf/main.py -d" ]
  timeout = "5s"
  name_override = "snmp_disk_stats"
  name_suffix = ""
  data_format = "json"
  tag_keys = [ "host", "disk_number"]

[[inputs.exec]]
  commands = [ "/etc/telegraf/scripts/readynas-to-telegraf/main.py -f" ]
  timeout = "5s"
  name_override = "snmp_fan_stats"
  name_suffix = ""
  data_format = "json"
  tag_keys = [ "host", "fan_number"]

[[inputs.exec]]
  commands = [ "/etc/telegraf/scripts/readynas-to-telegraf/main.py -t" ]
  timeout = "5s"
  name_override = "snmp_temperature_stats"
  name_suffix = ""
  data_format = "json"
  tag_keys = [ "host", "temperature_number"]

[[inputs.exec]]
  commands = [ "/etc/telegraf/scripts/readynas-to-telegraf/main.py -v" ]
  timeout = "5s"
  name_override = "snmp_raid_volume_stats"
  name_suffix = ""
  data_format = "json"
  tag_keys = [ "host", "volume_number"]

[[inputs.exec]]
  commands = [ "/etc/telegraf/scripts/readynas-to-telegraf/main.py -i" ]
  timeout = "5s"
  name_override = "snmp_interface_stats"
  name_suffix = ""
  data_format = "json"
  tag_keys = [ "host", "ifName"]

[[inputs.exec]]
  commands = [ "/etc/telegraf/scripts/readynas-to-telegraf/main.py -u" ]
  timeout = "5s"
  name_override = "snmp_uptime_stats"
  name_suffix = ""
  data_format = "json"
  tag_keys = [ "host" ]
```
