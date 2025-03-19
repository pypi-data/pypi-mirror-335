import yaml
import sys
import ansible_runner
import json
import time


install_play = [
    {
        "name": "Installation of needed software", 
        "hosts": "all",
        "tasks":
        [
            {
                "become": "true",
                "apt": "name=python3-pip state=present update_cache=true",
                "retries": "5",
                "delay": "30" 
            },
            
            {
                "name": "Installing QKD node",
                "become": "false", 
                "shell": "/usr/bin/pip install qd2-node"
            }
        ]
    }
]

provisioning_play = [
{
    "name": "Provisioning",
    "hosts": "all",
    "tasks":[
        {
            "name": "Copy file",
            "copy":{
                "dest": "{{py_env}}/python3 ~/site-packages/qd2_node/quditto_v2.yaml",
                "content": ""
            }
        }
    ]

},
]

start_receive_play = [
    {
    "name": "Receiver execution",
    "hosts": "",
    "tasks":[
        {
            "name": "Start receiver",
            "shell":{
                "chdir": "{{py_env}}/python3 ~/site-packages/qd2_node",
                "cmd": ""
            },
        }
    ]

},    
]

start_http_receptor_play = [
    {
    "name": "Repector execution",
    "hosts": "",
    "tasks":[
        {
            "name": "Start receptor",
            "shell":{
                "chdir": "{{py_env}}/python3 ~/site-packages/qd2_node",
                "cmd": ""
            },
        }
    ]

},    
]

stop_play = [
    {
    "name": "Stop",
    "hosts": "all",
    "tasks":[
        {
            "name": "Stopping receive script",
            "shell":{
                "chdir": "{{py_env}}/python3 ~",
                "cmd": "pkill -f 'receive_q2.py'"
            },                   
        },
        {
            "name": "Stopping receptor script",
            "shell":{
                "chdir": "{{py_env}}/python3 ~",
                "cmd": "pkill -f 'http_receptor.py'"
            },                   
        }
    ]

},
]

def get_provisioning_play(content):
    play = provisioning_play
    play[0]["tasks"][0]["copy"]["content"] = content
    return play

def get_receiver_play(host):
    play = start_receive_play
    play[0]["hosts"] = host
    play[0]["tasks"][0]["shell"]["cmd"] = "python3 receive_qd2.py "+str(host)
    return play

def get_receptor_play(host, IP):
    play = start_receive_play
    play[0]["hosts"] = host
    play[0]["tasks"][0]["shell"]["cmd"] = "python3 http_receptor.py.py "+str(IP)+" 8000 "+str(host)
    return play

def install(config_file, inv_file):
    # Added a small delay to ensure that the virtual node is up
    print('Sleeping to avoid errors in the Ansible ssh connection....')
    time.sleep(30)

    ansible_runner.run(playbook = install_play, inventory = inv_file)

    p = get_provisioning_play(config_file)
    ansible_runner.run(playbook = p, inventory=inv_file)
        

# This function starts simulaqron in every node in the inventory file
def run(config_file, inv_file):
    nodes_array = config_file["nodes"]

    nodes = {}
    for i, node in enumerate(nodes_array):
        node_name = node["node_name"]
        nodes[node_name] = node

    for node in nodes:
        rp = get_receiver_play(node)
        ansible_runner.run(playbook = rp, inventory=inv_file)
        hp =get_receptor_play(node, nodes[node]["node_ip"])
        ansible_runner.run(playbook = hp, inventory = inv_file)
    
def stop(inv_file):
    ansible_runner.run(playbook = stop_play, inventory = inv_file)
