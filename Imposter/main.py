import nmap
from getmac import get_mac_address
from telegram import Bot
import asyncio

IP = "192.168.1.1"
KNOWN_DEVICES = ["00:05:90:71:92:7f","52:c9:6a:cd:fe","18:4d:f6:92:7f","ed:b9:ab:7e:4d"]
TELEGRAM_BOT_TOKEN = "8001561514:AAHNzloH9N3nA8L7gIe6XMCcYFTUVqWLocE"
CHAT_ID = "8285139094"

class NetworkScanner:

    def __init__(self,ip:str):
        self.ip =ip
        self.connected_devices=set()

    def scan(self):
        network = f"{self.ip}/24"
        nm= nmap.PortScanner()

        while True:
            nm.scan(hosts=network,arguments='-sn')
            host_list = nm.all_hosts()


            for host in host_list:
                mac = get_mac_address(ip=host)
                print(mac)

                if mac and mac not in self.connected_devices and mac not in KNOWN_DEVICES:
                    print("new Device found")
                    self.notify_new_devices(mac)
                    self.connected_devices.add(mac)

    async def send_telegarm_message(self,bot,chat_id,message):
        await bot.send_message(chat_id=chat_id,text=message)

    def notify_new_devices(self,mac):
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        asyncio.run(self.send_telegarm_message(bot,CHAT_ID,f"New Device Connected! MAC address:{mac}"))


if __name__== "__main__":
    scanner = NetworkScanner(IP)
    scanner.scan()