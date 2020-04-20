#!/usr/bin/python3

## @file main.py
# @brief Main program
# @author Ross A. Stewart
# @copyright 2019-2020
# @date 18th April 2020
# @details
#
# This module executes methods which gather statistics from
# a Netgear ReadyNAS via SNMP
#
# Required libraries:
#   - os
#   - GetReadyNasStats
#       - From local module get_readynas_stats
#

import os
import argparse

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
