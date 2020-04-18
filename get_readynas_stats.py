## @file get_readynas_stats.py
# @brief Get stats via SNMP from a Netgear ReadyNAS
# @author Ross A. Stewart
# @copyright 2019-2020
# @par License
# MIT License
# @date 16th April 2020
# @details
#
# This module contains classes which gather statistics from Netgear ReadyNAS
# via SNMP
#
# Required libraries:
#   - SnmpQuery
#       - From local module snmp_utilities - [https://github.com/rosskouk/python_snmp_utilities]
#

from submodules.python_snmp_utilities.snmp_utilities import SnmpQuery


class GetReadyNasStats(SnmpQuery):
    """! @brief Netgear ReadyNAS Stats

    @details Get statistics from a Netgear ReadyNAS via SNMP
    """

    def __init__(self, host, community_string):
        """! @brief Constructor

        @param host STRING - The hostname of the ReadyNAS device
        @param community_string STRING - The SNMP community string set on the ReadyNAS device
        @details

        Sets required parameters
        """

        ## @var host
        # @brief STRING - The hostname of the ReadyNAS device
        self.host = host

        ## @var host
        # @brief STRING - The SNMP community string set on the ReadyNAS device
        self.community_string = community_string

    def process_readynas_disk_table(self):
        """! @brief Get disk information from a Netgear ReadyNAS

        @return True on success
        @return False on failure
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

        from a Netgear ReadyNAS and inserts them into InfluxDB
        """

        measurement_list = []  # Blank list to hold dictionaries of measurements

        disk_entries = self.get_next(self.host,
                                     [
                                         {'READYNASOS-MIB': 'diskNumber'},
                                         {'READYNASOS-MIB': 'ataError'},
                                         {'READYNASOS-MIB': 'diskState'},
                                         {'READYNASOS-MIB': 'diskTemperature'}
                                     ], self.construct_credentials(False, self.community_string))

        for disk_entry in disk_entries:
            # Iterate over list of measurements

            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = self.get_snmp_name(
                self.host, self.community_string)

            for key, value in disk_entry.items():
                # Iterate over measurement fields
                if self.get_brief_name(key) == 'diskNumber':
                    # Process diskNumber
                    fields['disk_number'] = value
                elif self.get_brief_name(key) == 'ataError':
                    # Process ataError
                    fields['ata_error_count'] = value
                elif self.get_brief_name(key) == 'diskState':
                    # Process diskState
                    if value == 'ONLINE':
                        # Disk is good
                        fields['disk_status'] = 0
                    else:
                        # Disk is bad
                        fields['disk_status'] = 1
                elif self.get_brief_name(key) == 'diskTemperature':
                    # Process diskTemperature
                    fields['disk_temperature'] = value
                else:
                    # Unexpected value found
                    raise ValueError(
                        'Unexpected SNMP value in method process_readynas_disk_table()')

            measurement_list.append(fields)  # Add the measurement to the list

        print(measurement_list)  # Print out the gathered statistics
