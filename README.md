### readynas-to-telegraf

Script to gather SNMP health and performance data from a Netgear ReadyNAS unit and pass it to the Telegraf exec plugin.  The information gathered is reformatted to make it more dashboard friendly.

#### Compatibility

The script has been tested on a ReadyNAS RN204 running firmware version 6.10.2

#### Installation

###### Python Dependencies

- PySNMP - https://pypi.org/project/pysnmp/
