import json
import os


'''
Written by Yang Ji
'''


def sr_flow_add(dpid, path, outport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":40,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"eth_type":2048,' \
                        '"icmpv4_type":%d'%(path+20)+',' \
                        '"ip_proto":1' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"DEC_NW_TTL"' \
                        '},' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":%d'%(outport) + '' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def icmp_source_routing():
    #edge switch
    for i in range(0,8):
        dpid = 0x300+i
        sr_flow_add(dpid, 0, 3)
        sr_flow_add(dpid, 1, 3)
        sr_flow_add(dpid, 2, 4)
        sr_flow_add(dpid, 3, 4)
        #sr_flow_add(dpid, 0,3)
        #sr_flow_add(dpid, 2,3)
        #sr_flow_add(dpid, 1,4)
        #sr_flow_add(dpid, 3,4)
    # Aggr switch
    for i in range(0,8):
        dpid = 0x200+i
        sr_flow_add(dpid, 0, 3)
        sr_flow_add(dpid, 1, 4)
        sr_flow_add(dpid, 2, 3)
        sr_flow_add(dpid, 3, 4)
        #sr_flow_add(dpid, 0,3)
        #sr_flow_add(dpid, 1,3)
        #sr_flow_add(dpid, 2,4)
        #sr_flow_add(dpid, 3,4)


icmp_source_routing()

