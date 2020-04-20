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
#
#   - GetReadyNasStats
#       - From local module get_readynas_stats
#

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

stats = GetReadyNasStats(readynas_host, readynas_snmp_community)  # Create a new GetReadyNasStats object

stats.process_readynas_disk_table()  # Get disk statistics
