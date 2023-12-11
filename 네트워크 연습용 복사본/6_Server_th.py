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
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #중복 오류 해결을 위한 코드

serverSocket.bind(ADDR)
serverSocket.listen(10)
print('서버가 시작되었습니다.')

def client_com(cs, addr):
    global user_info, rooms

    try:
        userInfo = cs.recv(BUFSIZE).decode()
        userID, countryName = userInfo.split(':')
        if countryName in rooms:
            user_info[cs] = (userID, countryName)
            rooms[countryName].add(cs)
            cs.send("Success".encode())
            print(f"User {userID} from {countryName} has entered the chat.")  # 사용자 입장 메시지
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
                
                print(f"User {userID} has left the chat.")  # 사용자 퇴장 메시지
                break


            elif msg.startswith('broadcast:'):
                all_clients = [socket for room in rooms.values() for socket in room]
                for socket in all_clients:
                    if socket != cs:
                        socket.send(msg.encode())

            # elif msg.startswith('broadcast:'):
            #     broadcast_msg = msg[len('broadcast:'):]  # 'broadcast:' 접두사 제거
            #     all_clients = [socket for room in rooms.values() for socket in room]
            #     for socket in all_clients:
            #         if socket != cs:
            #             try:
            #                 socket.send(broadcast_msg.encode())
            #             except Exception as e:
            #                 # 오류 처리
            #                 continue

                        


            elif msg.startswith('change_country:'):
                new_country = msg.split(':')[1].strip()
                if new_country in rooms:
                    old_country = user_info[cs][1]
                    rooms[old_country].remove(cs)
                    rooms[new_country].add(cs)
                    user_info[cs] = (user_info[cs][0], new_country)
                    cs.send(f"Country changed to {new_country}".encode())
                    print(f"User {userID} changed country from {old_country} to {new_country}.")  # 국가 변경 메시지
                else:
                    cs.send("Invalid country".encode())
            elif msg == 'show':
                user_list = "\n".join([f"{uid}: {country}" for _, (uid, country) in user_info.items()])
                cs.send(user_list.encode())
            else:
                current_country = user_info[cs][1]
                for socket in rooms[current_country]:
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
