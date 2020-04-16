## @namespace gather_readynas_stats
# @brief Get SNMP data from a Netgear ReadyNAS
# @author Ross A. Stewart
# @copyright 2019-2020
# @date 13th April 2020
# @details
#
# This module gathers bandwidth and health data from a
# Netgear ReadyNAS
#
# Required libraries:
#   - os
#       - Used to set paths for the script enabling the config file to be found
#   - yaml
#       - Used to read the configuration file - [https://pyyaml.org/]
#   - SnmpQuery
#       - From local module snmp_utilities
#   - InfluxDbOps
#       - From local package influxdb_utilities
#


import os

import yaml
from influxdb_utilities import InfluxDbOps
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

## @var influxdb_dbname
# @brief STRING - The InfluxDB password
influxdb_dbname = cfg['influxdb']['dbname']

## @var influxdb_host
# @brief STRING - The InfluxDB hostname
influxdb_host = cfg['influxdb']['host']

## @var influxdb_pass
# @brief STRING - The InfluxDB password
influxdb_pass = cfg['influxdb']['password']

## @var influxdb_port
# @brief INTEGER - The InfluxDB port number
influxdb_port = cfg['influxdb']['port']

## @var influxdb_user
# @brief STRING - The InfluxDB user
influxdb_user = cfg['influxdb']['user']

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

## @var influxdb
# @brief OBJECT - Instance of InfluxDbOps
# @details
# @link influxdb_utilities.InfluxDbOps InfluxDbOps Class @endlink
influxdb = InfluxDbOps(influxdb_host, influxdb_port,
                       influxdb_user, influxdb_pass, influxdb_dbname)


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

    # The name of the InfluxDB measurement to store the data in
    measurement_name = 'snmp_disk_stats'
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

        measurement = {}  # Define a blank dictionary to hold the measurement data
        tags = {}  # Define a blank dictionary to hold the tags
        fields = {}  # Define a blank dictionary to hold the fields

        # Get the timestamp for the measurement
        timestamp = influxdb.get_influxdb_timestamp()

        # Define the measurement name
        measurement['measurement'] = measurement_name
        tags['host'] = snmp.get_snmp_name(host, community_string)

        for key, value in disk_entry.items():
            # Iterate over measurement fields
            if snmp.get_brief_name(key) == 'diskNumber':
                # Process diskNumber
                tags['disk_number'] = value
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

            # Build the measurement
            measurement['tags'] = tags
            measurement['time'] = timestamp
            measurement['fields'] = fields

        measurement_list.append(measurement)  # Add the measurement to the list

    status = influxdb.influxdb_write(measurement_list)

    if status is True:
        # Operation succeeded
        return True
    else:
        # Operation failed
        return False


def process_readynas_fan_table(host, community_string):
    """! @brief Get fan information from a Netgear ReadyNAS

    @param host STRING - The host name or IP address of the device
    @param community_string STRING - The SNMP read only community string
    @return True on success
    @return False on failure
    @details

    Gets information required for the SNMP fans measurement:
      - The Fan Number
      - The Fan Speed (RPM)
      - The Fan Status
        - The ReadyNAS device returns this as a string, we convert it into an integer
          to ease monitoring.  We no return 0 for OK, 1 for failed

    from a Netgear ReadyNAS and inserts them into InfluxDB
    """

    # The name of the InfluxDB measurement to store the data in
    measurement_name = 'snmp_fan_stats'
    measurement_list = []  # Blank list to hold dictionaries of measurements

    fan_entries = snmp.get_next(host,
                                [
                                    {'READYNASOS-MIB': 'fanNumber'},
                                    {'READYNASOS-MIB': 'fanRPM'},
                                    {'READYNASOS-MIB': 'fanStatus'}
                                ], snmp.construct_credentials(False, community_string))

    for fan_entry in fan_entries:
        # Iterate over list of measurements

        measurement = {}  # Define a blank dictionary to hold the measurement data
        tags = {}  # Define a blank dictionary to hold the tags
        fields = {}  # Define a blank dictionary to hold the fields

        # Get the timestamp for the measurement
        timestamp = influxdb.get_influxdb_timestamp()

        # Define the measurement name
        measurement['measurement'] = measurement_name
        tags['host'] = snmp.get_snmp_name(host, community_string)

        for key, value in fan_entry.items():
            # Iterate over measurement fields
            if snmp.get_brief_name(key) == 'fanNumber':
                # Process fanNumber
                tags['fan_number'] = value
            elif snmp.get_brief_name(key) == 'fanRPM':
                # Process fanRPM
                fields['fan_speed_rpm'] = value
            elif snmp.get_brief_name(key) == 'fanStatus':
                # Process fanStatus
                if value == 'ok':
                    # Disk is good
                    fields['fan_status'] = 0
                else:
                    # Disk is bad
                    fields['fan_status'] = 1
            else:
                # Unexpected value found
                raise ValueError(
                    'Unexpected SNMP value in method process_readynas_fan_table()')

            # Build the measurement
            measurement['tags'] = tags
            measurement['time'] = timestamp
            measurement['fields'] = fields

        measurement_list.append(measurement)  # Add the measurement to the list

    status = influxdb.influxdb_write(measurement_list)

    if status is True:
        # Operation succeeded
        return True
    else:
        # Operation failed
        return False


def process_readynas_temperature_table(host, community_string):
    """! @brief Get temperature information from a Netgear ReadyNAS

    @param host STRING - The host name or IP address of the device
    @param community_string STRING - The SNMP read only community string
    @return True on success
    @return False on failure
    @details

    Gets information required for the SNMP temperatures measurement:
      - The Temperature Number
      - The Temperature (C)

    from a Netgear ReadyNAS and inserts them into InfluxDB
    """

    # The name of the InfluxDB measurement to store the data in
    measurement_name = 'snmp_temperature_measurements'
    measurement_list = []  # Blank list to hold dictionaries of measurements

    temperature_entries = snmp.get_next(host,
                                        [
                                            {'READYNASOS-MIB': 'temperatureNumber'},
                                            {'READYNASOS-MIB': 'temperatureValue'}
                                        ], snmp.construct_credentials(False, community_string))

    for temperature_entry in temperature_entries:
        # Iterate over list of measurements

        measurement = {}  # Define a blank dictionary to hold the measurement data
        tags = {}  # Define a blank dictionary to hold the tags
        fields = {}  # Define a blank dictionary to hold the fields

        # Get the timestamp for the measurement
        timestamp = influxdb.get_influxdb_timestamp()

        # Define the measurement name
        measurement['measurement'] = measurement_name
        tags['host'] = snmp.get_snmp_name(host, community_string)

        for key, value in temperature_entry.items():
            # Iterate over measurement fields
            if snmp.get_brief_name(key) == 'temperatureNumber':
                # Process temperatureNumber
                tags['temperature_number'] = value
            elif snmp.get_brief_name(key) == 'temperatureValue':
                # Process temperatureValue
                fields['temperature_celsius'] = value
            else:
                # Unexpected value found
                raise ValueError(
                    'Unexpected SNMP value in method process_readynas_temperature_table()')

            # Build the measurement
            measurement['tags'] = tags
            measurement['time'] = timestamp
            measurement['fields'] = fields

        measurement_list.append(measurement)  # Add the measurement to the list

    status = influxdb.influxdb_write(measurement_list)

    if status is True:
        # Operation succeeded
        return True
    else:
        # Operation failed
        return False


def process_readynas_volume_table(host, community_string):
    """! @brief Get volume information from a Netgear ReadyNAS

    @param host STRING - The host name or IP address of the device
    @param community_string STRING - The SNMP read only community string
    @return True on success
    @return False on failure
    @details

    Gets information required for the SNMP volumes measurement:
      - The Volume Number
      - The Volume Name
      - The Volume Status
        - The ReadyNAS returns strings, we translate these into integers as below:
            - 1 - REDUNDANT
            - 2 - DEGRADED
            - 3 - UNPROTECTED
            - 4 - DEAD
            - 5 - INACTIVE
            - 6 - UNKNOWN
      - The Volume Size (MB)
      - The Volume Free Space (MB)

    from a Netgear ReadyNAS and inserts them into InfluxDB
    """

    # The name of the InfluxDB measurement to store the data in
    measurement_name = 'snmp_volume_stats'
    measurement_list = []  # Blank list to hold dictionaries of measurements

    volume_entries = snmp.get_next(host,
                                   [
                                       {'READYNASOS-MIB': 'volumeNumber'},
                                       {'READYNASOS-MIB': 'volumeName'},
                                       {'READYNASOS-MIB': 'volumeStatus'},
                                       {'READYNASOS-MIB': 'volumeSize'},
                                       {'READYNASOS-MIB': 'volumeFreeSpace'}
                                   ], snmp.construct_credentials(False, community_string))

    for volume_entry in volume_entries:
        # Iterate over list of measurements

        measurement = {}  # Define a blank dictionary to hold the measurement data
        tags = {}  # Define a blank dictionary to hold the tags
        fields = {}  # Define a blank dictionary to hold the fields

        # Get the timestamp for the measurement
        timestamp = influxdb.get_influxdb_timestamp()

        # Define the measurement name
        measurement['measurement'] = measurement_name
        tags['host'] = snmp.get_snmp_name(host, community_string)

        for key, value in volume_entry.items():
            # Iterate over measurement fields
            if snmp.get_brief_name(key) == 'volumeNumber':
                # Process volumeNumber
                tags['volume_number'] = value
            elif snmp.get_brief_name(key) == 'volumeName':
                # Process volumeName
                fields['volume_name'] = value
            elif snmp.get_brief_name(key) == 'volumeStatus':
                # Process volumeStatus
                # - 1 - REDUNDANT
                # - 2 - DEGRADED
                # - 3 - UNPROTECTED
                # - 4 - DEAD
                # - 5 - INACTIVE
                # - 6 - UNKNOWN
                if value == 'REDUNDANT':
                    fields['volume_status'] = 1
                elif value == 'DEGRADED':
                    fields['volume_status'] = 2
                elif value == 'UNPROTECTED':
                    fields['volume_status'] = 3
                elif value == 'DEAD':
                    fields['volume_status'] = 4
                elif value == 'INACTIVE':
                    fields['volume_status'] = 5
                elif value == 'UNKNOWN':
                    fields['volume_status'] = 6

            elif snmp.get_brief_name(key) == 'volumeSize':
                # Process volumeSize
                fields['volume_size_mb'] = value
            elif snmp.get_brief_name(key) == 'volumeFreeSpace':
                # Process volumeFreeSpace
                fields['volume_free_mb'] = value
            else:
                # Unexpected value found
                raise ValueError(
                    'Unexpected SNMP value in method process_readynas_volume_table()')

            # Build the measurement
            measurement['tags'] = tags
            measurement['time'] = timestamp
            measurement['fields'] = fields

        measurement_list.append(measurement)  # Add the measurement to the list

    status = influxdb.influxdb_write(measurement_list)

    if status is True:
        # Operation succeeded
        return True
    else:
        # Operation failed
        return False


def process_readynas_interface_table(host, community_string):
    """! @brief Get interface information from a Netgear ReadyNAS

    @param host STRING - The host name or IP address of the device
    @param community_string STRING - The SNMP read only community string
    @return True on success
    @return False on failure
    @details

    Gets information required for the SNMP interfaces measurement.
    This includes fields from both the ifTable and ifXTable including
    byte, packet and error counters.  Only high capacity (HC) counters
    are queried for byte and packet counts.  The information is stored
    in an InfluxDB measurement.
    """

    # The name of the InfluxDB measurement to store the data in
    measurement_name = 'snmp_interface_stats'
    measurement_list = []  # Blank list to hold dictionaries of measurements

    interface_entries = snmp.get_next(host,
                                      [
                                          {'IF-MIB': 'ifIndex'},
                                          {'IF-MIB': 'ifName'},
                                          {'IF-MIB': 'ifType'},
                                          {'IF-MIB': 'ifAdminStatus'},
                                          {'IF-MIB': 'ifOperStatus'},
                                          {'IF-MIB': 'ifHCInOctets'},
                                          {'IF-MIB': 'ifHCInUcastPkts'},
                                          {'IF-MIB': 'ifHCInMulticastPkts'},
                                          {'IF-MIB': 'ifHCInBroadcastPkts'},
                                          {'IF-MIB': 'ifHCOutOctets'},
                                          {'IF-MIB': 'ifHCOutUcastPkts'},
                                          {'IF-MIB': 'ifHCOutMulticastPkts'},
                                          {'IF-MIB': 'ifHCOutBroadcastPkts'},
                                          {'IF-MIB': 'ifInDiscards'},
                                          {'IF-MIB': 'ifInErrors'},
                                          {'IF-MIB': 'ifOutDiscards'},
                                          {'IF-MIB': 'ifOutErrors'},

                                      ], snmp.construct_credentials(False, community_string))

    for interface_entry in interface_entries:
        # Iterate over list of measurements

        measurement = {}  # Define a blank dictionary to hold the measurement data
        tags = {}  # Define a blank dictionary to hold the tags
        fields = {}  # Define a blank dictionary to hold the fields

        # Get the timestamp for the measurement
        timestamp = influxdb.get_influxdb_timestamp()

        # Define the measurement name
        measurement['measurement'] = measurement_name
        tags['host'] = snmp.get_snmp_name(host, community_string)

        for key, value in interface_entry.items():
            # Iterate over measurement fields
            if snmp.get_brief_name(key) == 'ifName':
                # Process ifName
                tags[snmp.get_brief_name(key)] = value
            else:
                # Process all other fields
                fields[snmp.get_brief_name(key)] = value

            # Build the measurement
            measurement['tags'] = tags
            measurement['time'] = timestamp
            measurement['fields'] = fields

        measurement_list.append(measurement)  # Add the measurement to the list

    status = influxdb.influxdb_write(measurement_list)

    if status is True:
        # Operation succeeded
        return True
    else:
        # Operation failed
        return False


process_readynas_disk_table(readynas_host, readynas_snmp_community)
process_readynas_fan_table(readynas_host, readynas_snmp_community)
process_readynas_temperature_table(readynas_host, readynas_snmp_community)
process_readynas_volume_table(readynas_host, readynas_snmp_community)
process_readynas_interface_table(readynas_host, readynas_snmp_community)
