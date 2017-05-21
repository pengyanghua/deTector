import json
import os

def f_flow_add(dpid, inport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":50,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"in_port":%d'%inport+'' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def f_flow_remove(dpid, inport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":50,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"in_port":%d'%inport+'' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/delete'%flowadd_msg)

def f_flow_tuple_add(dpid, sip, sport, dip, dport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":50,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"ipv4_src":"%s"'%sip+',' \
                        '"ipv4_dst":"%s"'%dip+',' \
                        '"udp_src":%d'%sport+',' \
                        '"udp_dst":%d'%dport+',' \
                        '"ip_proto":17,' \
                        '"eth_type":2048' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    #print 'curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def f_flow_tuple_remove(dpid, sip, sport, dip, dport):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":1,' \
                    '"cookie_mask":1,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":50,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"ipv4_src":"%s"'%sip+',' \
                        '"ipv4_dst":"%s"'%dip+',' \
                        '"udp_src":%d'%sport+',' \
                        '"udp_dst":%d'%dport+',' \
                        '"ip_proto":17,' \
                        '"eth_type":2048' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    #print 'curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/delete'%flowadd_msg)

def f_loss_add(dpid, inport, loss):
    flowadd_msg =   '{"dpid":%d'%dpid + ','\
                    '"cookie":%d'%(10000+int(loss*10000)) + ',' \
                    '"cookie_mask":0xFFFF,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":50,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"in_port":%d'%inport+'' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/add'%flowadd_msg)

def f_loss_remove(dpid, inport, loss):
    flowadd_msg =   '{"dpid":%d'%dpid+','\
                    '"cookie":%d'%(10000+int(loss*10000)) + ',' \
                    '"cookie_mask":0xFFFF,' \
                    '"table_id":0,' \
                    '"idle_timeout":0,' \
                    '"hard_timeout":0,' \
                    '"priority":50,' \
                    '"flags":1,' \
                    '"match":{' \
                        '"in_port":%d'%inport+'' \
                        '},' \
                    '"actions":[' \
                        '{' \
                        '"type":"OUTPUT",' \
                        '"port":"CONTROLLER"' \
                        '}' \
                    ']' \
                    '}'
    #print flowadd_msg
    os.system('curl -X POST -d \'%s\' http://localhost:8080/stats/flowentry/delete'%flowadd_msg)

def f_clean_all(dpid):
    os.system('curl -X DELETE http://localhost:8080/stats/flowentry/clear/%d'%dpid)

def f_switch_fail(dpid):
    f_flow_add(dpid, 1)
    f_flow_add(dpid, 2)
    f_flow_add(dpid, 3)
    f_flow_add(dpid, 4)

def f_switch_recover(dpid):
    f_flow_remove(dpid, 1)
    f_flow_remove(dpid, 2)
    f_flow_remove(dpid, 3)
    f_flow_remove(dpid, 4)

def f_link_fail(s_dpid, s_port, d_dpid, d_port):
    f_flow_add(s_dpid, s_port)
    f_flow_add(d_dpid, d_port)

def f_link_recover(s_dpid, s_port, d_dpid, d_port):
    f_flow_remove(s_dpid, s_port)
    f_flow_remove(d_dpid, d_port)

def f_loss_fail(s_dpid, s_port, d_dpid, d_port, loss_rate):
    print "sid 0x%x sp %d did 0x%x dp %d loss %f"%(s_dpid, s_port, d_dpid, d_port, loss_rate)
    f_loss_add(s_dpid, s_port, loss_rate)
    f_loss_add(d_dpid, d_port, loss_rate)

def f_loss_recover(s_dpid, s_port, d_dpid, d_port, loss_rate):
    f_loss_remove(s_dpid, s_port, loss_rate)
    f_loss_remove(d_dpid, d_port, loss_rate)

def f_tuple_fail(dpid, sip, sport, dip, dport):
    f_flow_tuple_add(dpid, sip, sport, dip, dport)

def f_tuple_fail(dpid, spi, sport, dip, dport):
    f_flow_tuple_remove(dpid, sip, sport, dip, dport)

#f_switch_fail(0x100)
#f_switch_recover(0x100)

#f_link_fail(0x100, 1, 0x200,3)
#f_link_recover(0x100, 1, 0x200,3)

#f_flow_tuple_add(0x100, "10.0.0.2/255.255.255.0", 80,  "10.1.0.2/255.255.255.0", 80)
#f_flow_tuple_remove(0x100, "10.0.0.2/255.255.255.0", 80,  "10.1.0.2/255.255.255.0", 80)

#f_loss_add(0x201, 3, 0.01305)
#f_loss_remove(0x100, 1, 0.5)
#f_loss_fail(0x100, 1, 0x200, 3, 0.2)
#f_loss_recover(0x100, 1, 0x200, 3, 0.2)


#f_link_fail(0x200, 1, 0x300,3)
#f_link_recover(0x200, 1, 0x300,3)

