import json
import os


'''
Written by Yang Ji
'''


def sr_flow_add(dpid, ip):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":9,' \
                    '"cookie_mask":0xffff,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":45,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"eth_type":2048,' \
                        '"ipv4_dst": "%s"'%ip+'' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def icmp_source_routing():
    #edge switch
    for i in range(0,8):
        dpid = 0x300+i
        sr_flow_add(dpid, "10.%d.%d.7"%(3,i))
    # Aggr switch
    for i in range(0,8):
        dpid = 0x200+i
        sr_flow_add(dpid, "10.%d.%d.7"%(2,i))
    for i in range(0,4):
        dpid = 0x100+i
        sr_flow_add(dpid, "10.%d.%d.7"%(1,i))

icmp_source_routing()

