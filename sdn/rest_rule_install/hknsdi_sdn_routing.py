import json
import os


'''
Written by Yang Ji
'''


def sr_flow_add(dpid, ecn, outport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":10,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"eth_type":2048' +','\
                        '"ip_ecn":%d'%ecn +''\
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"DEC_NW_TTL"' \
                        '},' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":%d'%outport+'' \
                        '}' \
                    ']' \
                    '}'
    print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def ip_flow_add(dpid, ip, outport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":20,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"eth_type":2048' +',' \
                        '"ipv4_dst": "%s"'%ip+'' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"DEC_NW_TTL"' \
                        '},' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":%d'%outport+'' \
                        '}' \
                    ']' \
                    '}'
    print flowadd_msg
    #print 'curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def source_routing():
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

def ip_routing():
    #core switch
    for i in range(0,4):
        dpid = 0x100 +i
        ip_flow_add(dpid, "10.0.0.2", 1)
        ip_flow_add(dpid, "10.1.0.2", 2)
        ip_flow_add(dpid, "10.2.0.2", 3)
        ip_flow_add(dpid, "10.3.0.2", 4)
        ip_flow_add(dpid, "10.0.1.2", 1)
        ip_flow_add(dpid, "10.1.1.2", 2)
        ip_flow_add(dpid, "10.2.1.2", 3)
        ip_flow_add(dpid, "10.3.1.2", 4)
        #ip_flow_add(dpid, "10.0.0.0/255.255.0.0", 1)
        #ip_flow_add(dpid, "10.1.0.0/255.255.0.0", 2)
        #ip_flow_add(dpid, "10.2.0.0/255.255.0.0", 3)
        #ip_flow_add(dpid, "10.3.0.0/255.255.0.0", 4)
    #aggr switch
    for i in range(0,8):
        dpid = 0x200 + i
        podid = i/2
        ip_flow_add(dpid, "10.%d.0.2"%podid, 1)
        ip_flow_add(dpid, "10.%d.1.2"%podid, 2)
    #edge switch
    for i in range(0,8):
        dpid = 0x300 + i
        podid = i/2
        ip_flow_add(dpid, "10.%d.%d.2"%(podid,i%2), 1)


# install defailt routing policy
def install_default_routing():
    source_routing()
    ip_routing()


install_default_routing()
