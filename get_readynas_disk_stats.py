## @namespace get_readynas_disk_stats
# @brief Get disk stats via SNMP from a Netgear ReadyNAS
# @author Ross A. Stewart
# @copyright 2019-2020
# @date 16th April 2020
# @details
#
# This module gathers disk statistics from a Netgear ReadyNAS
# via SNMP and outputs it as JSON data which can be read by
# telegraf
#
# Required libraries:
#   - os
#       - Used to set paths for the script enabling the config file to be found
#   - yaml
#       - Used to read the configuration file - [https://pyyaml.org/]
#   - SnmpQuery
#       - From local module snmp_utilities
#   - GeneralUtilities
#       - From local module general_utilities
#

import os

import yaml

from snmp_utilities import SnmpQuery

#
# Setup paths
#

## @var program_directory
# @brief STRING - The absolute path to the directory the running script is in
program_directory = os.path.dirname(__file__)

#
# Read the configuration file
#

try:
    with open(program_directory + '/config.yaml', 'r') as ymlfile:
        ## @var cfg
        # @brief DICTIONARY - A dictionary representing the YAML configuration file
        cfg = yaml.load(ymlfile)

except FileNotFoundError:
    print('Configuration file not found.')
    raise

except:
    print('An error occurred when reading the configuration file.\n')
    raise

#
# Set Variables
#

## @var readynas_host
# @brief STRING - The hostname of the ReadyNAS device
readynas_host = cfg['readynas']['host']

## @var readynas_snmp_community
# @brief STRING - The SNMP community string of the ReadyNAS device
readynas_snmp_community = cfg['readynas']['community']

## @var snmp
# @brief OBJECT - Instance of SnmpQuery
# @details
# @link snmp_utilities.SnmpQuery SnmpQuery Class @endlink
snmp = SnmpQuery()


def process_readynas_disk_table(host, community_string):
    """! @brief Get disk information from a Netgear ReadyNAS

    @param host STRING - The host name or IP address of the device
    @param community_string STRING - The SNMP read only community string
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

    disk_entries = snmp.get_next(host,
                                 [
                                     {'READYNASOS-MIB': 'diskNumber'},
                                     {'READYNASOS-MIB': 'ataError'},
                                     {'READYNASOS-MIB': 'diskState'},
                                     {'READYNASOS-MIB': 'diskTemperature'}
                                 ], snmp.construct_credentials(False, community_string))

    for disk_entry in disk_entries:
        # Iterate over list of measurements

        fields = {}  # Define a blank dictionary to hold the fields

        # Store the hostname
        fields['host'] = snmp.get_snmp_name(host, community_string)

        for key, value in disk_entry.items():
            # Iterate over measurement fields
            if snmp.get_brief_name(key) == 'diskNumber':
                # Process diskNumber
                fields['disk_number'] = value
            elif snmp.get_brief_name(key) == 'ataError':
                # Process ataError
                fields['ata_error_count'] = value
            elif snmp.get_brief_name(key) == 'diskState':
                # Process diskState
                if value == 'ONLINE':
                    # Disk is good
                    fields['disk_status'] = 0
                else:
                    # Disk is bad
                    fields['disk_status'] = 1
            elif snmp.get_brief_name(key) == 'diskTemperature':
                # Process diskTemperature
                fields['disk_temperature'] = value
            else:
                # Unexpected value found
                raise ValueError(
                    'Unexpected SNMP value in method process_readynas_disk_table()')

        measurement_list.append(fields)  # Add the measurement to the list

    print(measurement_list)


# Execute the function
process_readynas_disk_table(readynas_host, readynas_snmp_community)
