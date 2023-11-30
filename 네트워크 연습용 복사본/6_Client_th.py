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
        user_input = input("Enter 'User_ID: Country(1. south korea 2. north korea 3. china 4. japan 5. mongolia 6. taiwan) \n(ex. Cho: south korea) \n")
        try:
            user_id, country = map(str.strip, user_input.split(':'))
            if country in ["south korea", "north korea", "china", "japan", "mongolia", "taiwan"]:
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
print("""Commands,
  show: 현재 국가의 채팅방 모든 사용자 ID를 알려줍니다.
  change_country: 국가명 - 국가를 변경합니다. ex) change_country: south korea
  exit: 채팅방을 종료합니다.
""")

user_id, country = user_info.split(':')

def listen_from_server():
    while True:
        message = clientSocket.recv(1024).decode()
        if message:
            print("Received, " + message) 

t = Thread(target=listen_from_server)
t.daemon = True
t.start()

while True:
    sendData = input("채팅: ")
    if sendData:
        if sendData.startswith("change_country"):
            try:
                _, new_country = sendData.split(":", 1)
                new_country = new_country.strip()
                if new_country in ["south korea", "north korea", "china", "japan", "mongolia", "taiwan"]:
                    clientSocket.send(f"change_country:{new_country}".encode())
                else:
                    print("Invalid country format.")
            except ValueError:
                print("Invalid command format. Use 'change_country: CountryName'.")

        elif sendData == "show":
            clientSocket.send(sendData.encode())
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"send: {user_id}/ {country}/ {timestamp}/ {sendData}"
            clientSocket.send(formatted_message.encode())
            print(formatted_message)

    if sendData == 'exit':
        break

clientSocket.close()
print('클라이언트 종료')