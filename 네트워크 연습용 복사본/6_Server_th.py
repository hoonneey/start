from socket import *
from threading import Thread

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

clientSockets = set()
user_info = {}
rooms = {"south korea": set(), "north korea": set(), "china": set(), "japan": set(), "mongolia": set(), "taiwan": set()}

serverSocket = socket(AF_INET, SOCK_STREAM) # TCP 연결을 위한 소켓을 생성
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #주소 재사용 옵션을 설정
serverSocket.bind(ADDR) #주소 바인딩: 서버 소켓을 특정 호스트 주소와 포트에 바인딩
serverSocket.listen(10)
print('서버가 시작되었습니다.')

#클라이언트 요청 처리
def client_com(cs, addr): #클라이언트와의 통신을 처리하는 함수. 클라이언트와 연결된 소켓, 주소.
    global user_info, rooms #전역 변수 선언

    try: #사용자 정보(사용자 ID 및 국가명)를 수신하고, 처리
        userInfo = cs.recv(BUFSIZE).decode()
        userID, countryName = userInfo.split(':')
        if countryName in rooms:
            user_info[cs] = (userID, countryName) #클라이언트 소켓(cs)을 키로 하여 사용자 ID와 국가명을 user_info에 저장.  (cs, (userID, countryName))
            rooms[countryName].add(cs) #현재 클라이언트를 해당 국가의 채팅방에 추가
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
            if msg == 'exit': #클라이언트 종료 처리
                break

            #메시지 브로드캐스트
            elif msg.startswith('broadcast:'):
                all_clients = [socket for room in rooms.values() for socket in room]
                for socket in all_clients:
                    if socket != cs:
                        socket.send(msg.encode())
                        

            #국가 변경 및 사용자 정보 조회
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
    countryName = user_info[cs][1] if cs in user_info else None
    if countryName and countryName in rooms and cs in rooms[countryName]:
        rooms[countryName].remove(cs)
    if cs in user_info:
        print(f"User {user_info[cs][0]} has left the chat.")  # 사용자 퇴장 메시지
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
