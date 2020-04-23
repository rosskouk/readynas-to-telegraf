#!/usr/bin/python3

## @file main.py
# @brief Main program
# @author Ross A. Stewart
# @copyright 2020
# @par License
# MIT License
# @date 18th April 2020
# @details
#
# This module executes methods which gather statistics from
# a Netgear ReadyNAS via SNMP.
#
#
# Required libraries:
#   - argparse
#   - json
#   - os
#   - yaml
#   - GetReadyNasStats
#       - From local module get_readynas_stats
#
#
# You should have received a copy of the MIT license with
# this file. If not, please or visit :
# https://github.com/rosskouk/readynas-to-influxdb/blob/master/LICENSE


import argparse
import json
import os

import yaml

from get_readynas_stats import GetReadyNasStats

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

#
# Parse CLI arguments
#

## @var arg_parser
# @brief OBJECT - An instance of ArgumentParser to process CLI options
arg_parser = argparse.ArgumentParser(description='Get SNMP statistics from a Netgear ReadyNAS')

## @var arg_group
# @brief OBJECT - A mutually exclusive ArgumentParser group
# @details This group holds all CLI options and ensures that only one is chosen
arg_group = arg_parser.add_mutually_exclusive_group(required=True)

## @cond INTERNAL
# Have Doxygen skip this line
arg_group.add_argument('-d', '--disks', action='store_true', dest='disks', help='get disk statistics')
arg_group.add_argument('-f', '--fans', action='store_true', dest='fans', help='get fan statistics')
arg_group.add_argument('-t', '--temp', action='store_true', dest='temp', help='get temperature statistics')
arg_group.add_argument('-v', '--volumes', action='store_true', dest='volumes', help='get volume statistics')
arg_group.add_argument('-i', '--interfaces', action='store_true', dest='interfaces', help='get interface statistics')
# @endcond

## @var args
# @brief OBJECT - An object containing the parsed CLI arguments
# @details This group holds all CLI options and ensures that only one is chosen
args = arg_parser.parse_args()


#
# Execute methods
#

if args.disks is True:
    stats = GetReadyNasStats(readynas_host, readynas_snmp_community)  # Create a new GetReadyNasStats object
    stats.process_readynas_disk_table()  # Get disk statistics

if args.fans is True:
    stats = GetReadyNasStats(readynas_host, readynas_snmp_community)  # Create a new GetReadyNasStats object
    stats.process_readynas_fan_table()  # Get fan statistics

if args.temp is True:
    stats = GetReadyNasStats(readynas_host, readynas_snmp_community)  # Create a new GetReadyNasStats object
    stats.process_readynas_temperature_table()  # Get temperature statistics

if args.volumes is True:
    stats = GetReadyNasStats(readynas_host, readynas_snmp_community)  # Create a new GetReadyNasStats object
    stats.process_readynas_volume_table()  # Get volume statistics

if args.interfaces is True:
    stats = GetReadyNasStats(readynas_host, readynas_snmp_community)  # Create a new GetReadyNasStats object
    print(json.dumps(stats.get_snmp_interfaces()))  # Get interface statistics
