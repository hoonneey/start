""" # 6_client_exit
# 사용자로부터 exit 문자열이 올때까지 계속 서버로 전송
# exit 문자열을 수신하면 서버에게 exit 전송하고 연결 종료

from socket import *
#from select import *
import sys
from time import ctime
from threading import Thread

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)
          
clientSocket = socket(AF_INET, SOCK_STREAM)  # 서버에 접속하기 위한 소켓을 생성한다.

try:
    clientSocket.connect(ADDR)  # 서버에 접속을 시도한다.

except  Exception as e:
    print('%s:%s' %ADDR)
    sys.exit()
       
print('연결 성공')

def listen_from_server():
    while True:
        message = clientSocket.recv(1024).decode()
        print("\nBroadcast message:" + message)
        
# make a thread that listens for messages to this client & print them
t = Thread(target=listen_from_server)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

while True:
    print("입력 데이터 : ")
    sendData = input()
    clientSocket.send(sendData.encode())
    if sendData == 'exit': # exit라는 메세지를 받으면 종료
        break
#    data = clientSocket.recv(BUFSIZE)
 #   print('받은 데이터 : ', data.decode())
clientSocket.close()
print('종료')
 """

from socket import *
import sys
from threading import Thread

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    clientSocket.connect(ADDR)
except Exception as e:
    print('%s:%s' % ADDR)
    sys.exit()

group_id = input("Enter your initial group ID: ")
clientSocket.send(group_id.encode())

def listen_from_server():
    while True:
        message = clientSocket.recv(1024).decode()
        print("\nReceived message: " + message)

t = Thread(target=listen_from_server)
t.daemon = True
t.start()

while True:
    sendMessage = input("Enter message, 'show_groups' to list groups, or 'change_group:new_group_id' to change group: ")
    
    if sendMessage == "show_groups":
        clientSocket.send(sendMessage.encode())
    elif sendMessage.startswith("change_group:"):
        new_group_id = sendMessage.split(':')[1]
        group_id = new_group_id
        clientSocket.send(sendMessage.encode())
    else:
        message = group_id + ':' + sendMessage
        clientSocket.send(message.encode())

    if sendMessage == 'exit':
        break


clientSocket.close()


