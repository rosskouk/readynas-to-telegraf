## @namespace snmp_utilities
# @brief SNMP Utility Classes
# @author Ross A. Stewart
# @copyright 2019-2020
# @date 13th April 2020
# @details
#
# This module allows access to classes which provide SNMP
# querying functionality using the pySNMP library.  Based
# on code from https://www.ictshore.com/sdn/python-snmp-tutorial
#
# Required libraries:
#   - pysnmp - https://github.com/etingof/pysnmp
#
from pysnmp import hlapi


class SnmpQuery:
    """! @brief SNMP query class

    @details This class provides methods to query SNMP devices
    """

    def cast(self, value):
        """! @brief Correctly set the type of the given variable

        @param value - MIXED The value to be cast
        @return MIXED The value correctly cast to it's type
        @details

        Attempts to cast value as and integer, float then string.
        if a ValueError or TypeError occurs the next attempt it made.
        If the value cannot be cast as any of the types it is returned
        as is.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    return str(value)
                except (ValueError, TypeError):
                    pass

        return value

    def construct_credentials(self, v3, credentials):
        """! @brief Construct SNMP credentials

        @param v3 BOOL - True of SNMP v3 is in use, False otherwise
        @param credentials STRING|ARRAY - A community string or an array of SNMP v3 credential information
        @return OBJECT - A CommunityData or UsmUserData object is returned
        @exception NotImplementedError - Triggered if SNMP v3 is used
        """

        if(v3 is False):
            community_string = hlapi.CommunityData(credentials)
            return community_string
        else:
            raise NotImplementedError

    def construct_object_types(self, list_of_oids):
        """! @brief Construct a list of PySNMP ObjectType objects for use in an SNMP query

        @param list_of_oids LIST - list of OIDs, or textual names to query
        @return LIST - List of PySNMP ObjectType objects
        @details

        Takes a list of OIDs or textual representations and creates PySNMP
        ObjectType objects for them.  OIDs are string entries in the list, textual
        representations are dictionary entries with the MIB as the key and field
        as the value. Example:
        @code
        [
            {'READYNASOS-MIB': 'fanRPM'},
            '1.3.6.1.4.1.4526.22.4.1.2.1',
            ...
        ]
        @endcode
        """

        object_types = []
        for oid in list_of_oids:
            if type(oid) is str:
                object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
            if type(oid) is dict:
                for key, value in oid.items():
                    object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(key, value)))

        return object_types

    def fetch(self, handler):
        """! @brief Loop over a handler and return queried values

        @param handler - OBJECT Preconfigured snmp query object
        @return LIST of DICTIONARIES - List of dictionaries containing the identifier and value of each query
        @exception RuntimeError - Triggered when an SNMP error occurs
        """

        result = []
        for (error_indication,
                error_status,
                error_index,
                var_binds) in handler:
            try:
                if not error_indication and not error_status:
                    items = {}
                    for var_bind in var_binds:
                        items[str(var_bind[0].prettyPrint())] = self.cast(var_bind[1])
                    result.append(items)
                else:
                    raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
            except StopIteration:
                break

        return result

    def get(self, target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        """! @brief Get a single SNMP value

        @param target STRING - The SNMP target
        @param oids LIST - OID, or textual name to query
        @param credentials OBJECT - PySNMP CommunityData or UsmUserData object see below
        @param port INTEGER - The SNMP port number
        @param engine OBJECT - PySNMP SnmpEngine object
        @param context OBJECT - PySNMP ContextData object
        @return DICTIONARY - Single value dictionary containing the first result
        @details

        Creates a handler which performs an SNMP get request and passes it to fetch().
        The credentials parameter differs depending on which version of SNMP is
        being used examples:
        - SNMP v1 or v2c
          - hlapi.CommunityData('public')
        - SNMP v3
          - hlapi.UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey',
                              authProtocol=hlapi.usmHMACSHAAuthProtocol, privProtocol=hlapi.usmAesCfb128Protocol)
        """

        handler = hlapi.getCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            *self.construct_object_types(oids),  # Asterisk automatically expands list of objects
            lexicographicMode=False
        )

        return self.fetch(handler)

    def get_next(self, target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        """! @brief Get a single SNMP value

        @param target STRING - The SNMP target
        @param oids LIST - OIDs, or textual names to query
        @param credentials OBJECT - PySNMP CommunityData or UsmUserData object see below
        @param port INTEGER - The SNMP port number
        @param engine OBJECT - PySNMP SnmpEngine object
        @param context OBJECT - PySNMP ContextData object
        @return DICTIONARY - Single value dictionary containing the first result
        @details

        Creates a handler which performs an SNMP get request and passes it to fetch(). The credentials parameter differs depending on
        which version of SNMP is being used, examples:
        - SNMP v1 or v2c
          - hlapi.CommunityData('public')
        - SNMP v3
          - hlapi.UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey',
                              authProtocol=hlapi.usmHMACSHAAuthProtocol, privProtocol=hlapi.usmAesCfb128Protocol)
        """
        handler = hlapi.nextCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            *self.construct_object_types(oids),
            lexicographicMode=False
        )

        return self.fetch(handler)
