## @file get_readynas_stats.py
# @brief Get stats via SNMP from a Netgear ReadyNAS
# @author Ross A. Stewart
# @copyright 2020
# @par License
# MIT License
# @date 16th April 2020
# @details
#
# This module contains classes which gather statistics from Netgear ReadyNAS
# via SNMP
#
# Required libraries:
#   - json
#   - SnmpUtility
#       - From local module snmp_utilities - [https://github.com/rosskouk/python_snmp_utilities]
#
#
# You should have received a copy of the MIT license with
# this file. If not, please or visit :
# https://github.com/rosskouk/readynas-to-telegraf/blob/master/LICENSE


import json

from submodules.python_snmp_utilities.snmp_utilities import SnmpUtility


class GetReadyNasStats(SnmpUtility):
    """! @brief Netgear ReadyNAS Stats

    @details Get statistics from a Netgear ReadyNAS via SNMP
    """

    def __init__(self, *args):
        """! @brief Constructor

        @param args LIST - Arguments to pass to the parent constructor, hostname and community string
        @details

        Passes the SNMP device hostname and community string to the parent constructor
        """

        super().__init__(*args)

    def get_readynas_uptime(self):
        """! @brief Get the uptime from a Netgear ReadyNAS

        @details

        The uptime is printed in JSON format which can be imported by the Telegraf exec
        plugin.
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements
        device_name = self.get_snmp_name()
        host_uptime = self.get_snmp_uptime()
        fields = {}

        # Store the hostname
        fields['host'] = device_name['sysName']
        fields['uptime'] = host_uptime['sysUpTimeInstance']

        measurement_list.append(fields)  # Add to the measurement list

        print(json.dumps(measurement_list))  # Print out the gathered statistics

    def process_readynas_disk_table(self):
        """! @brief Get disk information from a Netgear ReadyNAS

        @details

        Gets information required for the SNMP disks measurement:
        - The Disk Number
        - ATA Error Count
        - The Disk State
            - The READYNASOS-MIB states that values are 0 for online and 1 for offline, however
            strings are returned instead, we convert the strings to the correct integer values
            to allow better monitoring and processing of data
        - The Disk Temperature
            - This is reported in Celsius although the MIB states the value is reported in
            Fahrenheit

        The information is printed in JSON format which can be imported by the Telegraf exec
        plugin.
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements

        oids = [
            'READYNASOS-MIB::diskNumber',
            'READYNASOS-MIB::ataError',
            'READYNASOS-MIB::diskState',
            'READYNASOS-MIB::diskTemperature'
        ]

        disk_entries = self.bulkwalk(oids)

        device_name = self.get_snmp_name()

        for disk_entry in disk_entries:
            # Iterate over list of measurements

            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = device_name['sysName']

            for key, value in disk_entry.items():
                # Iterate over measurement fields
                if key == 'diskNumber':
                    # Process diskNumber
                    fields['disk_number'] = value
                elif key == 'ataError':
                    # Process ataError
                    fields['ata_error_count'] = value
                elif key == 'diskState':
                    # Process diskState
                    if value == 'ONLINE':
                        # Disk is good
                        fields['disk_status'] = 0
                    else:
                        # Disk is bad
                        fields['disk_status'] = 1
                elif key == 'diskTemperature':
                    # Process diskTemperature
                    fields['disk_temperature'] = value
                else:
                    # Unexpected value found
                    raise ValueError(
                        'Unexpected SNMP value in method process_readynas_disk_table()')

            measurement_list.append(fields)

        print(json.dumps(measurement_list))  # Convert measurements to JSON and print them

    def process_readynas_fan_table(self):
        """! @brief Get fan information from a Netgear ReadyNAS

        @details

        Gets information required for the SNMP fans measurement:
        - The Fan Number
        - The Fan Speed (RPM)
        - The Fan State
            - This is returned as a string 'ok', this is converted to an integer 0 for OK
              1 for FAULTY

        The information is printed in JSON format which can be imported by the Telegraf exec
        plugin.
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements

        oids = [
            'READYNASOS-MIB::fanNumber',
            'READYNASOS-MIB::fanRPM',
            'READYNASOS-MIB::fanStatus'
        ]

        fan_entries = self.bulkwalk(oids)

        device_name = self.get_snmp_name()

        for fan_entry in fan_entries.values():
            # Iterate over list of measurements

            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = device_name['sysName']

            for key, value in fan_entry.items():
                # Iterate over measurement fields
                if key == 'fanNumber':
                    # Process fanNumber
                    fields['fan_number'] = value
                elif key == 'fanRPM':
                    # Process fanRPM
                    fields['fan_speed_rpm'] = value
                elif key == 'fanStatus':
                    # Process fanStatus
                    if value == 'ok':
                        # fan is good
                        fields['fan_status'] = 0
                    else:
                        # fan is bad
                        fields['fan_status'] = 1
                else:
                    # Unexpected value found
                    raise ValueError(
                        'Unexpected SNMP value in method process_readynas_fan_table()')

            measurement_list.append(fields)  # Add the measurement to the list

        print(json.dumps(measurement_list))  # Print out the gathered statistics

    def process_readynas_interface_table(self):
        """! @brief Get interface information from a Netgear ReadyNAS

        @details

        Gets information required for the SNMP interfaces measurement as returned
        by get_snmp_interfaces()

        The information is printed in JSON format which can be imported by the Telegraf exec
        plugin.
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements

        interface_entries = self.get_snmp_interfaces()

        device_name = self.get_snmp_name()

        for interface_entry in interface_entries:
            # Iterate over list of measurements

            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = device_name['sysName']

            for key, value in interface_entry.items():
                # Iterate over measurement fields
                fields[key] = value

            measurement_list.append(fields)

        print(json.dumps(measurement_list))  # Convert measurements to JSON and print them

    def process_readynas_temperature_table(self):
        """! @brief Get temperature information from a Netgear ReadyNAS

        @details

        Gets information required for the SNMP temperatures measurement:
        - The Temperature Number
        - The Temperature Value (C)
          - The READYNASOS-MIB states that units are in Fahrenheit, this is incorrect

        The information is printed in JSON format which can be imported by the Telegraf exec
        plugin.
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements

        oids = [
            'READYNASOS-MIB::temperatureNumber',
            'READYNASOS-MIB::temperatureValue'
        ]

        temperature_entries = self.bulkwalk(oids)

        device_name = self.get_snmp_name()

        for temperature_entry in temperature_entries.values():
            # Iterate over list of measurements

            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = device_name['sysName']

            for key, value in temperature_entry.items():
                # Iterate over measurement fields
                if key == 'temperatureNumber':
                    # Process temperatureNumber
                    fields['temperature_number'] = value
                elif key == 'temperatureValue':
                    # Process temperatureValue
                    fields['temperature_celsius'] = value
                else:
                    # Unexpected value found
                    raise ValueError(
                        'Unexpected SNMP value in method process_readynas_temperature_table()')

            measurement_list.append(fields)  # Add the measurement to the list

        print(json.dumps(measurement_list))  # Print out the gathered statistics

    def process_readynas_volume_table(self):
        """! @brief Get volume information from a Netgear ReadyNAS

        @details

        Gets information required for the SNMP volumes measurement:
        - The Volume Number
        - The Volume RAID Level
        - The Volume Status
          - The READYNASOS-MIB states that the following string
            values are generated:
            - REDUNDANT = 0
            - DEGRADED = 1
            - UNPROTECTED = 2
            - DEAD = 3
            - INACTIVE = 4
            - UNKNOWN = 5
        - The Volume Total Size
            - Reported in MB
        - The Volume Free Space
            - Reported in MB
        - The Volume Used Space
            - Calculated via: \f$Volume Used Space = Volume Total Size - Volume Free Space\f$

            These values are translated into integers to ease monitoring

        The information is printed in JSON format which can be imported by the Telegraf exec
        plugin.
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements

        oids = [
            'READYNASOS-MIB::volumeNumber',
            'READYNASOS-MIB::volumeRAIDLevel',
            'READYNASOS-MIB::volumeStatus',
            'READYNASOS-MIB::volumeSize',
            'READYNASOS-MIB::volumeFreeSpace'
        ]

        volume_entries = self.bulkwalk(oids)

        device_name = self.get_snmp_name()

        for volume_entry in volume_entries.values():
            # Iterate over list of measurements

            free_space = None  # Variable to hold free space value
            total_space = None  # Variable to hold total volume size
            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = device_name['sysName']

            for key, value in volume_entry.items():
                # Iterate over measurement fields
                if key == 'volumeNumber':
                    # Process volumeNumber
                    fields['volume_number'] = value
                elif key == 'volumeRAIDLevel':
                    # Process volumeRAIDLevel
                    fields['volume_raid_level'] = value
                elif key == 'volumeStatus':
                    # Process volumeStatus
                    if value == 'REDUNDANT':
                        # Volume OK
                        fields['volume_status'] = 0
                    elif value == 'DEGRADED':
                        # Volume is degraded - WARN
                        fields['volume_status'] = 1
                    elif value == 'UNPROTECTED':
                        # Volume is unprotected - WARN
                        fields['volume_status'] = 2
                    elif value == 'DEAD':
                        # Volume is dead - CRIT
                        fields['volume_status'] = 3
                    elif value == 'INACTIVE':
                        # Volume is inactive - CRIT
                        fields['volume_status'] = 4
                    elif value == 'UNKNOWN':
                        # Volume status is unknown - CRIT
                        fields['volume_status'] = 5
                elif key == 'volumeSize':
                    # Process volumeSize

                    total_space = value  # Store the total space to allow calculation of used space
                    fields['volume_total_size_mb'] = value

                elif key == 'volumeFreeSpace':
                    # Process volumeFreeSpace

                    free_space = value  # Store the free space to allow calculation of used space
                    fields['volume_free_space_mb'] = value
                else:
                    # Unexpected value found
                    raise ValueError(
                        'Unexpected SNMP value in method process_readynas_volume_table()')

                if total_space is not None and free_space is not None:
                    # Calculate used space and add the value to the measurement
                    used_space = total_space - free_space
                    fields['volume_used_space_mb'] = used_space

            measurement_list.append(fields)  # Add the measurement to the list

        print(json.dumps(measurement_list))  # Print out the gathered statistics
