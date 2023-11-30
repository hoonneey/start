from socket import *
from threading import Thread

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

clientSockets = set()
user_info = {}
rooms = {"south korea": set(), "north korea": set(), "china": set(), "japan": set(), "mongolia": set(), "taiwan": set()}

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(10)
print('서버가 시작되었습니다.')

def client_com(cs, addr):
    global user_info, rooms

    try:
        userInfo = cs.recv(BUFSIZE).decode()
        userID, countryName = userInfo.split(':')
        if countryName in ["south korea", "north korea", "china", "japan", "mongolia", "taiwan"]:
            user_info[cs] = (userID, countryName)
            rooms[countryName].add(cs)
            cs.send("Success".encode())
        else:
            cs.send("Fail".encode())
            return
    except:
        cs.send("Fail".encode())
        return

    while True:
        try:
            msg = cs.recv(BUFSIZE).decode()
            if msg == 'exit':
                break
            elif msg.startswith('change_country:'): # 이 부분 다시
                new_country = msg.split(':')[1]
                if new_country in rooms:
                    old_country = user_info[cs][1]
                    rooms[old_country].remove(cs)
                    rooms[new_country].add(cs)
                    user_info[cs] = (user_info[cs][0], new_country)
                    cs.send(f"Country changed to {new_country}".encode())
                else:
                    cs.send("Invalid country".encode())

            elif msg == 'show':
                user_list = "\n".join([f"{uid}: {country}" for _, (uid, country) in user_info.items()])
                cs.send(user_list.encode())
            else:
                for socket in rooms[countryName]:
                    if socket != cs:
                        socket.send(f"{msg}".encode())
        except:
            break

    cs.close()
    rooms[countryName].remove(cs)
    del user_info[cs]

while True:
    clientSocket, addr_info = serverSocket.accept()
    print('connection successful', addr_info)
    clientSockets.add(clientSocket)
    t = Thread(target=client_com, args=(clientSocket, addr_info))
    t.daemon = True
    t.start()

for cs in clientSockets:
    cs.close()
serverSocket.close()
