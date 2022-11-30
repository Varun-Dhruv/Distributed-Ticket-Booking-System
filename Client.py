import socket
import argparse
import json
parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, help="Enter IP address of server",default="127.0.0.1")
parser.add_argument("port", type=int, help="Enter Port number")
args = parser.parse_args()

HOST = args.ip
PORT = args.port

def getMovies():
      while True:

        print(
            '''
1. Films in theater 
2. Get Film Location By Time
3. Exit
4. Book a seat
'''
        )
        print("Enter your choice: ", end='')
        choice = int(input())
        if choice == 1:
            Films = (proxy.view_Films())
            for Film in Films:
                for Film_id in Film:
                    print("{:<15}".format(Film_id), end="\t")
                print("\n")
        elif choice == 2:
            name = input('Enter Film ID to rent your Film:').strip()
            timings = input('Enter the time of Film').strip()
            Filmlist = (proxy.getFilmsInfo(timings, name))
            if (len(Filmlist) == 0):
                print("No Films available at this time")
                continue
            print("The Film is available in: ")
            for Film in Filmlist:
                print(Film)
        elif choice == 3:
            print('Thank you! Visit us again!')
            break
        elif choice == 4:
            name = input('Enter Film ID to rent your Film:').strip()
            return json.dumps({ "operation":"read" ,"name":name})
        else:
            print("Wrong choice! Enter correct choice")

def getPostInfoFromUser():
    post_title = input("Enter Title for Post : ")
    post_description = input("Enter Description for Post : ")

    return json.dumps({
        "title": post_title,
        "description": post_description
    })
    
_data= getMovies()
#_data = getPostInfoFromUser()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = bytes(_data, 'utf-8')
    print(data)
    s.sendall(data)
print(f"Post Sent !!")