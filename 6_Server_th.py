""" # 6_server_thd
# 다중 클라이언트로 부터 메시지를 받아서 브로드캐스트
# 클라이언트가 exit 문자열이 보내올때까지 계속 수신
# exit 문자열을 수신하면 while 문 탈출하여 연결종료

from socket import *    # import socket 으로 하면 오류 
from select import *
from threading import Thread

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

# 연결된 client의 소켓 집합 set of connected client sockets
clientSockets = set()

# 소켓 생성
serverSocket = socket(AF_INET, SOCK_STREAM) 
##     socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# 소켓 주소 정보 할당
serverSocket.bind(ADDR)
print('바인드')

# 연결 수신 대기 상태
serverSocket.listen(10)
print('대기')

def client_com(cs):
    # 클라이언트로부터 메시지를 가져옴
    while True:
        try:  # 아래 문장 무조건 실행
            msg = cs.recv(BUFSIZE).decode()
            #print('recieve data : ',msg)
        except Exception as e:  # 위 문장 에러 처리: client no longer connected
            print(f"Error:{e}")
            clientSockets.remove(cs)
        else:  # 위 문장 에러 없을 시 실행
            if msg == 'exit': # exit라는 메세지를 받으면 정상종료
                cs.close()
                clientSockets.remove(cs)
                break
            print('broadcast data : ',msg)
            i=1;
            for socket in clientSockets: # broadcast
                socket.send(msg.encode())
                print(i)
                i=i+1

# 연결 수락
while True:
    clientSocekt, addr_info = serverSocket.accept()
    print('연결 수락: client 정보 ', addr_info)
    clientSockets.add(clientSocekt)
    t = Thread(target = client_com, args=(clientSocekt,))
    t.daemon = True
    t.start()

# 소켓 종료
for cs in clientSockets:
    cs.close()
serverSocket.close()
print('종료') """

from socket import *
from threading import Thread

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

client_info = {}  # 클라이언트 소켓과 그룹 ID를 저장하는 딕셔너리

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(10)


active_groups = set()  # 활성화된 그룹을 추적하는 집합

def client_com(cs):
    global active_groups
    group_id = client_info[cs]
    active_groups.add(group_id)  # 그룹 추가

    while True:
        try:
            msg = cs.recv(BUFSIZE).decode()
        except Exception as e:
            print(f"Error: {e}")
            del client_info[cs]
            cs.close()
            break

        if msg == 'exit':
            del client_info[cs]
            cs.close()
            break
        if msg.startswith("change_group:"):
            _, new_group_id = msg.split(':')
            active_groups.discard(group_id)  # 이전 그룹 제거
            active_groups.add(new_group_id)  # 새 그룹 추가
            client_info[cs] = new_group_id
            group_id = new_group_id
            continue

        if msg == "show_groups":
            response = "Active groups: " + ", ".join(active_groups)
            cs.send(response.encode())
            continue

        group_id, message = msg.split(':', 1)
        for socket in client_info:
            if client_info[socket] == group_id:
                socket.send(msg.encode())

    active_groups.discard(group_id)

                

while True:
    clientSocket, addr_info = serverSocket.accept()
    group_id = clientSocket.recv(BUFSIZE).decode()
    client_info[clientSocket] = group_id
    t = Thread(target=client_com, args=(clientSocket,))
    t.daemon = True
    t.start()

serverSocket.close()
