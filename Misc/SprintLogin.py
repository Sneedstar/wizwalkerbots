import asyncio
import ctypes
from ctypes import *

from wizwalker import WizWalker, ClientHandler

user32 = ctypes.WinDLL("user32.dll")

with open('accounts.txt') as fileVar:
    accounts = fileVar.read().splitlines()

async def start_clients(walker, clients,  account, i):

    if len(account.split(':')) == 4:
        username, password, x, y = account.split(':')
    elif len(account.split(':')) == 2:
        username, password = account.split(':')
    else:
        await walker.close

    clients[i].title = f"[{username}] Wizard101"
    clients[i].login(username, password)
    #if x and y:
        #user32.MoveWindow(clients[i].window_handle, x, y, bRepaint=True)


async def main():

    walker = WizWalker()

    for i in range(len(accounts)):
        ClientHandler.start_wiz_client()
    while len(clients := walker.get_new_clients()) < len(accounts):
        await asyncio.sleep(1)
    await asyncio.gather(*[start_clients(walker, clients, account, i) for i, account in enumerate(accounts)]) 

    await walker.close()

# Start
if __name__ == "__main__":
    asyncio.run(main())