#!/usr/bin/env python
# -*- coding: UTF-8 -*-

### LICENSE BSD ###
# Copyright (c) 2011, Salvador Girones, Abiquo
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Abiquo nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
###
#
# This script creates all DHCP leases from Abiquo database
#
##

import os
def main():
    c = os.popen('mysql kinton -e "select i.mac, i.name, IF(v.default_network,v.default_network,0), IF(i.configureGateway,i.configureGateway,0), i.ip, IF(n.gateway,n.gateway,0), IF(n.netmask,n.netmask,0), IF(n.primary_dns,n.primary_dns,0), IF(n.secondary_dns,n.secondary_dns,0) from ip_pool_management i, rasd_management r, network_configuration n, vlan_network v where i.idManagement = r.idManagement AND r.idVM IS NOT NULL AND i.vlan_network_id = v.vlan_network_id AND v.network_configuration_id = n.network_configuration_id;"')

    for l in c.readlines():
        if ":" in l:
            mac, name, is_private, configure_gw, ip, gw, netmask, dns1, dns2 = l.split()

            lease = "host %s {\n" % (name)
            lease += "    dynamic;\n"
            lease += "    hardware ethernet %s;\n"%(mac)
            lease += "    fixed-address %s;\n"%(ip)
            lease += "        supersede subnet-mask = %s;\n"%(ip_to_hex(netmask))
            #Gateway
            if int(configure_gw):
                lease += "        supersede routers = %s;\n"%(ip_to_hex(gw))

            #Dns
            dns = "        supersede domain-name-servers = concat ("
            if dns1 != "0":
                dns += "%s, "%(ip_to_hex(dns1))
            if dns2 != "0":
                dns += "%s)\n"%(ip_to_hex(dns2))
            else:
                dns += ")\n"

            lease += dns

            #Close lease
            lease += "}\n\n"
            print lease

def ip_to_hex(ip):
    ip = ip.split('.')
    ip_hex = ':'.join((hex(int(i))[2:] for i in ip))
    return ip_hex

if __name__ == "__main__":
    main()
