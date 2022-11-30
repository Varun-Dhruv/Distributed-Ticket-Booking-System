import sys

from xmlrpc.server import SimpleXMLRPCServer
import argparse
from time import time
from xmlrpc.client import ServerProxy
NETWORK = {
    "db_node_1": ("127.0.0.1", 5500),
    "db_node_2": ("127.0.0.1", 6600),
    "db_node_3": ("127.0.0.1", 7700),
}

class DBNode:
    def __init__(self, pid, pid_node_mapping, is_beacon_node=False):
        # this nodes pid
        self.pid = pid
        # set of all nodes pid in the network
        # so that we can judge whether to execute or not
        # this mapping is a dict and has "pid" as a key
        # and proxy RPC objects as values
        self.pid_node_mapping = pid_node_mapping
        # CRS (Critical Resource Server) rpc proxy
        self.is_beacon_node = is_beacon_node
        
    def write(self, data):
        print(f"[{round(time() * 1000)}] --> Writing Data to {self.pid}.db")
        print("Data => ", data)
        # logic to write in db
        with open(f"{self.pid}.db", "a") as f:
            f.write(f"[{round(time() * 1000)}] > {data}\n")
        
        # if this is a beacon node then forward data to
        # other databases
        if self.is_beacon_node:

            for pid, node_proxy in self.pid_node_mapping.items():
                # pass data to be written for data consistency
                node_proxy.write(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pid", type=str, help="Enter pid (db_node_1, db_node_2,db_node_3)")
    
    parser.add_argument("--is_beacon", type=bool,
                        help="if true then node acts as a beacon DB node",default=False)
    args = parser.parse_args()
    PID = args.pid
    IS_BEACON_NODE = args.is_beacon
        # create a RPC server running on a node
    server = SimpleXMLRPCServer(
        NETWORK[PID], allow_none=True, logRequests=False)
        # get all server proxy's
    pid_mapping = dict()
    for pid, addr in NETWORK.items():
        if pid == PID:
            continue
        pid_mapping[pid] = ServerProxy(f"http://{addr[0]}:{addr[1]}")
        
    server.register_instance(DBNode(
        PID, pid_mapping, is_beacon_node=IS_BEACON_NODE))
        
    try:
        if IS_BEACON_NODE:
            print("Starting as Beacon Node")
        
        print("Starting RPC Server...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)