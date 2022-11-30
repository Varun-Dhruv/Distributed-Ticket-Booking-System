from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from threading import Timer, Thread
from time import time
import socketserver
import argparse
import sys
NETWORK = {
    "node_1": ("127.0.0.1", 5000),
    "node_2": ("127.0.0.1", 6000),
    "node_3": ("127.0.0.1", 7000),
}
CRS = ("127.0.0.1", 4000)

SERVER_INSTANCE = None

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(4096).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        SERVER_INSTANCE.execute(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

class RPCServer:
    def __init__(self, pid, pid_node_mapping, CRS):
        # this nodes pid
        self.pid = pid
        # set of all nodes pid in the network
        # so that we can judge whether to execute or not
        # this mapping is a dict and has "pid" as a key
        # and proxy RPC objects as values
        self.pid_node_mapping = pid_node_mapping
        # CRS (Critical Resource Server) rpc proxy
        self.CRS = CRS
        # this queue will save to whom we have to send request
        # after out execution in critical section is finished
        self.request_queue = []
        # reply set to store pids from whom this node has
        # got reply

        self.reply_set = set()
        # time in seconds after which this process
        # indent to execute critical section
        # if "None" then this process doesn't want
        # to execute
        self.execute_at = None
        self.task_done = True
        self.data = None
        # if exetute_after:
        # self.execute_at = time() + exetute_after
        # # schedule task to execute after given amount of time
        # self.timer = Timer(exetute_after, self.execute)
        # self.timer.start()
        # self.task_done = False
    def request(self, timestamp: float, remote_node_pid: str):
        """
        RPC method to request access for shared resource
        across the resource
        Params:
        timestamp: seconds passed since an epoch
        pid: process id which requested access
        """
        print(f"[{round(time() * 1000)}] REQUEST --> {remote_node_pid}({round(timestamp*1000)})")
        # first check if this node wants to execute critical section
        # if yes then compair timestamps
        # if timestamp < self.execute_at then send reply
        if self.task_done or timestamp < self.execute_at:
            node = self.pid_node_mapping[remote_node_pid]
            node.reply(self.pid)
            return
        # else don't send reply just now
        # add remote_pid in queue and wait till this nodes

        # execution is finished,
        # for now add remote_pid in queue
        self.request_queue.append(remote_node_pid)
        
    def reply(self, rpid):
        # add rpid to self.reply_set
        self.reply_set.add(rpid)
        print(f"[{round(time() * 1000)}] REPLY --> {rpid}")
        # check if this process is waiting for critical
        # section and if yes then check if all replies
        # are received
        if self.execute_at:
            if set(self.pid_node_mapping.keys()) == self.reply_set:
                # if True then continue execute
                self.execute(after_replay=True)

    def execute(self, data=None, after_replay=False):
        # first send request to all nodes
        if not after_replay and data:
            self.execute_at = time()
            self.task_done = False
            self.data = data
            
            for rpid, node in self.pid_node_mapping.items():
                if rpid == self.pid:
                    continue
                # request all nodes
                timestamp = time()
                node.request(timestamp, self.pid)

        # now wait for all reply's
        if set(self.pid_node_mapping.keys()) == self.reply_set:
        # now we are allowed to execute in critical section
        # print("Before Execute => ", self.data)
            self.CRS.execute_task_in_critical(self.pid, self.data)
            self.task_done = True
            self.data = None

            print(f"[{round(time()*1000)}] Critical Section Resource Released\n\n")

        # after this process has completed execution
        # reply to everyone in queue
            for rpid in self.request_queue:
                self.pid_node_mapping[rpid].reply(self.pid)
            
            # clear reply_set after execution
            self.reply_set = set()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pid", type=str, help="Enter pid (node_1, node_2, node_3)")
    
    args = parser.parse_args()
    
    PID = args.pid

    # create a RPC server running on a node
    server = SimpleXMLRPCServer(NETWORK[PID], allow_none=True, logRequests=False)
    
    # get all server proxy's
    pid_mapping = dict()
    for pid, addr in NETWORK.items():
        if pid == PID:
            continue

        pid_mapping[pid] = ServerProxy(f"http://{addr[0]}:{addr[1]}")

    crs_proxy = ServerProxy(f"http://{CRS[0]}:{CRS[1]}")

    SERVER_INSTANCE = RPCServer(PID, pid_mapping, crs_proxy)
    server.register_instance(SERVER_INSTANCE)
    
    # TCP socket
    HOST, PORT = NETWORK[PID]
    loadbalancer_socket = socketserver.TCPServer(
        (HOST, PORT + 1),MyTCPHandler
    )

    try:
        print("Starting Servers...")
        threads = [
            Thread(target=server.serve_forever),
            Thread(target=loadbalancer_socket.serve_forever)
        ]
        
        for th in threads:
            th.start()
            print(f"Server {th} Started")
        
        print("=" * 50)
        for th in threads:
            th.join()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)