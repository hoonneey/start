from socket import *
import sys
from threading import Thread
from datetime import datetime

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

def get_user_info():
    while True:
        user_input = input("Enter 'User_ID: Country(1. Korea 2. Japan 3. China 4. Mongolia 5. Taiwan) (ex. Cho:Korea). \n")
        try:
            user_id, country = map(str.strip, user_input.split(':'))
            if country in ["Korea", "Japan", "China", "Mongolia", "Taiwan"]:
                return f"{user_id}:{country}"
            else:
                print("Fail, 다시 입력해주세요.") #입력 형식 오류(:때문)
        except ValueError:
            print("Fail, 다시 입력해주세요.") #국가 입력 오류(국가 이름 때문)

clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    clientSocket.connect(ADDR)
except Exception as e:
    print('%s:%s' % ADDR)
    sys.exit()
user_info = get_user_info() # 'User_ID:Country' 형태로 정보를 받음
clientSocket.send(user_info.encode())
response = clientSocket.recv(BUFSIZE).decode()

if response == "Success":
    print(f"Success, {user_info} 입장했습니다.")
else:
    print("Fail, 다시 입력해주세요.")
    sys.exit()

user_id, country = user_info.split(':')

def listen_from_server():
    while True:
        message = clientSocket.recv(1024).decode()
        if message:
            print("\nReceived message: " + message) # 이 부분 체크

t = Thread(target=listen_from_server)
t.daemon = True
t.start()
while True:
    sendData = input("채팅: ") # 사용자(국가): 로 바꾸기
    if sendData:
        if sendData == "show":
            clientSocket.send(sendData.encode())
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"send: {user_id}/ {country}/ {timestamp}\n{sendData}"
            clientSocket.send(formatted_message.encode())
            print({formatted_message})

    if sendData == 'exit':
        break

clientSocket.close()
print('클라이언트 종료')