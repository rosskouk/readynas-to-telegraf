## @namespace influxdb_utilities
# @brief InfluxDB Classes
# @author Ross A. Stewart
# @copyright 2020
# @date 15th April 2020
# @details
#
# This module provides classes which allow interactions with InfluxDB
# instances.
#
# Required libraries:
#   - datetime
#   - InfluxDBClient
#       - Found in the influxdb package
#

import datetime

from influxdb import InfluxDBClient


class InfluxDbOps:
    """! @brief InfluxDB Operations Class

    @details This class provides methods to connect and query InfluxDB
    instances
    """

    def __init__(self, host, port, user, password, dbname):
        """! @brief Class constructor

        @param host STRING - The InfluxDB hostname
        @param port INTEGER - The InfluxDB port number
        @param user STRING - The username to connect to InfluxDB with
        @param password STRING - The password to connect to InfluxDB with
        @param dbname STRING - The InfluxDB database to use
        @details

        Sets the InfluxDB hostname, port number, username, password and
        database name
        """

        ## @var host
        # @brief STRING - The InfluxDB hostname
        self.host = host

        ## @var port
        # @brief INTEGER - The InfluxDB port number
        self.port = port

        ## @var user
        # @brief STRING - The username to connect to InfluxDB with
        self.user = user

        ## @var password
        # @brief STRING - The password to connect to InfluxDB with
        self.password = password

        ## @var dbname
        # @brief STRING - The InfluxDB database to use
        self.dbname = dbname

    def get_influxdb_timestamp(self):
        """! @brief Generate an InfluxDB compatible timestamp

        @return STRING - The generated timestamp
        @details

        Generates a timestamp in the format 2009-11-10T23:00:00Z
        """

        time = datetime.datetime.now()
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')

        return timestamp

    def influxdb_connect(self):
        """! @brief Connect to an InfluxDB instance

        @return OBJECT Returns an instance of an InfluxDB client object
        """

        client = InfluxDBClient(self.host, self.port,
                                self.user, self.password, self.dbname)

        return client

    def influxdb_write(self, points):
        """! @brief Write points to an InfluxDB measurement

        @param points STRING - Correctly formatted list of Python dictionaries containing the points to write
        @return True on success
        @return False on failure

        @details

        Writes the data contained in the points parameter to an InfluxDB instance
        points should contain a list of Python dictionaries one dictionary per point,
        example:
        @code
        [
          {
            "measurement": "snmp_disk_stats",
            "tags": {
              "host": "bigbang",
              "disk_number": 4
            },
            "time": "2020-04-15T16:03:53",
            "fields": {
              "ata_error_count": 16,
              "disk_status": 0,
              "disk_temperature": 35
            }
          }
        ]
        @endcode
        """

        try:
            client = self.influxdb_connect()
            status = client.write_points(
                points, time_precision='s', protocol='json')

            if status is True:
                return True
            else:
                return False

        except:
            print('Unexpected error in function influxdb_write')
            raise

        finally:
            del client
