import sys
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import argparse
from time import time
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import mysql.connector
import socket

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="db"
)

mycursor = mydb.cursor()


def addData(movieID, movieName):
    sql = "INSERT INTO movies (movieID,movieName) VALUES (%s,%s)"
    # sql = "INSERT INTO movies2 (movieID,genre,seats,movieName) VALUES (%s,%s,%s,%s)"

    val = (movieID, movieName)
    mycursor.execute(sql, val)
    mydb.commit()
    msg = "Movie data inserted."
    return msg


def fetchData():
    Lst = []
    mycursor.execute("SELECT * FROM movies")
    myresult = mycursor.fetchall()
    for x in myresult:
        Lst.append(x)
    return Lst


class CRS:
    def __init__(self, pid, beacon_proxy):
        self.pid = pid
        self.beacon_proxy = beacon_proxy

    def execute_task_in_critical(self, rpid, data):
        print(f"[{round(time() * 1000)}] --> Data Sent By {rpid}")
        print("Data Received => ", data)
        # write data on DFS
        print(data)
        self.beacon_proxy.write(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ip", type=str, help="Enter IP Address of Server",
        default="127.0.0.1"
    )
    parser.add_argument("port", type=int, help="Enter Port Number")
    parser.add_argument("beacon_host", type=str,
                        help="Ip address of Beacon DB node")

    parser.add_argument("beacon_port", type=int,
                        help="Port number of Beacon DB node")

    args = parser.parse_args()
    HOST = args.ip
    PORT = args.port
    BEACON_HOST = args.beacon_host
    BEACON_PORT = args.beacon_port
    BEACON_PROXY = ServerProxy(f"http://{BEACON_HOST}:{BEACON_PORT}")

    # create a RPC server running on a node
    server = SimpleXMLRPCServer(
        (HOST, PORT), allow_none=True, logRequests=False)
    server.register_instance(CRS("CRS_Server", BEACON_PROXY))

    try:
        print("Starting RPC Server...")
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)
