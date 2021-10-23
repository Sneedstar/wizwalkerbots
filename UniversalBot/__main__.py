import asyncio
from time import time

from wizwalker.constants import Keycode
from wizwalker.extensions.wizsprinter import WizSprinter

from utils import decide_heal, go_through_dialog
from wiz_fighter import WizFighter

async def setup(client):
    print(f"[{client.title}] Activating Hooks")
    await client.activate_hooks()
    await client.mouse_handler.activate_mouseless()
    await client.send_key(Keycode.PAGE_DOWN, 0.1)
    await client.use_potion_if_needed(health_percent=20, mana_percent=5)

async def tp_to_p1(client, p1):
    p1pos = await p1.body.position()
    await client.teleport(p1pos)
    await asyncio.sleep(0.3)
    await client.send_key(Keycode.W, 0.1)
    await client.send_key(Keycode.D, 0.1)
    await asyncio.sleep(0.2)

async def tp_to_start(client, start, yaw, start_zone):
    print(f'[{client.title}] Tping to start')
    await client.teleport(start, yaw)
    while await client.zone_name() != start_zone:
        await client.send_key(Keycode.S, 0.25)
        await client.send_key(Keycode.D, 0.1)
        try:
            await client.mouse_handler.click_window_with_name('centerButton')
        except ValueError:
            await asyncio.sleep(0.01)
    print(f'[{client.title}] Going back to sigil')
    while not await client.is_in_npc_range():
        await client.send_key(Keycode.S, 0.25)

async def main(sprinter):
    # Register clients
    sprinter.get_new_clients()
    clients = sprinter.get_ordered_clients()
    p1, p2, p3, p4 = [*clients, None, None, None, None][:4]
    for i, p in enumerate(clients, 1):
        p.title = "p" + str(i)

    # Hook activation
    await asyncio.gather(*[setup(p) for p in clients])
    start_zone = await p1.zone_name()

    instance = False
    if await p1.is_in_npc_range():
        instance = True
        print("Farming Instance")

    Total_Count = 0
    total = time()
    while True:
        start = time()

        await asyncio.gather(*[decide_heal(p) for p in clients]) 

        if instance: 
            for client in clients:
                while await client.is_in_npc_range():
                    await asyncio.sleep(0.4)
                    await client.send_key(Keycode.X, 0.1)
            await asyncio.gather(*[p.wait_for_zone_change() for p in clients])

            await asyncio.sleep(1.4)
            dungeon_start = await p1.body.position()
            dungeon_yaw = await p1.body.yaw()

        # Porting to p1 to mob, then porting rest to p1
        await p1.tp_to_closest_mob()
        await asyncio.sleep(0.1)
        await p1.send_key(Keycode.W, 0.1)
        await asyncio.sleep(0.3)
        await asyncio.gather(*[tp_to_p1(p, p1) for p in clients])

        # Battle
        battles = []
        for client in clients:
            battles.append(WizFighter(client))
        await asyncio.gather(*[battle.wait_for_combat() for battle in battles])
        print("Combat Ended")

        # Checking if clients got sent into dialogue after battle
        await asyncio.sleep(1)
        for client in clients:
            if await client.is_in_dialog():
                await go_through_dialog(client)

        # Restarting run
        if instance:
            await asyncio.gather(*[tp_to_start(p, dungeon_start, dungeon_yaw, start_zone) for p in clients])
        else:
            await asyncio.sleep(0.4)
            await asyncio.gather(*[p.send_key(Keycode.S, 0.1) for p in clients])
            await asyncio.sleep(4.5)
        
        # Potions
        print("Using potions if needed")
        await asyncio.gather(*[p.use_potion_if_needed(health_percent=20, mana_percent=5) for p in clients])
        await asyncio.sleep(1)

        # Time
        Total_Count += 1
        print("------------------------------------------------------")
        print("The Total Amount of Runs: ", Total_Count)
        print("Time Taken for run: ", round((time() - start) / 60, 2), "minutes")
        print("Total time elapsed: ", round((time() - total) / 60, 2), "minutes")
        print("Average time per run: ", round(((time() - total) / 60) / Total_Count, 2), "minutes")
        print("------------------------------------------------------")


# Error Handling
async def run():
    sprinter = WizSprinter()

    try:
        await main(sprinter)
    except:
        import traceback

        traceback.print_exc()

    await sprinter.close()


# Start
if __name__ == "__main__":
    asyncio.run(run())
