#!/bin/bash
 # Program:
 #       This program add entry to all the switches in a mininet topo
 # History:
 # 2015-4-12 zp First release

# PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:~/bin
# export PATH

# ENTRY_FILE="VdpSimpleEntry.json" 


# while_read_LINE_bottm () 
# {
# 	while read LINE
# 	do
# 		taken="$LINE";

# 		head="$(echo $taken | cut -c 1)"
		

# 		if [[ "$head" == '#' ]]; then
# 			DPID="$(echo $taken | cut -c 2-)"
# 			echo "DPID=$DPID"
# 		elif [[ "$head" == '{' ]]; then
# 			echo "$taken" | jq .
# 		fi

# 	done  < $ENTRY_FILE
# }

# while_read_LINE_bottm;
#"ip_ecn":2,"eth_type":34525\



# Written by Yang Ji


curl -X POST -d '{\
	"dpid": 0x201,\
	"cookie":1,\
	"cookie_mask":1,\
	"table_id":0,\
	"idle_timeout":30,\
	"hard_timeout":30,\
	"priority":11111,\
	"flags":1,\
	"match":{\
		"ip_ecn":2,\
                "eth_type":2048\
	},\
	"actions":[\
		{\
		 "type":"OUTPUT",\
		 "port":2\
		 }\
	]\
}' http://localhost:8080/stats/flowentry/add

