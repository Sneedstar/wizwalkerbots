import asyncio
import pathlib
from time import time

from wizwalker.constants import Keycode
from wizwalker.extensions.wizsprinter import SprintyCombat, CombatConfigProvider, WizSprinter

from utils import decide_heal, logout_and_in

async def main(sprinter):
    # Register clients
    sprinter.get_new_clients()
    clients = sprinter.get_ordered_clients()
    p1, p2, p3, p4 = [*clients, None, None, None, None][:4]
    for i, p in enumerate(clients, 1):
        p.title = "p" + str(i)

    # Hook activation
    for p in clients: 
        print(f"[{p.title}] Activating Hooks")
        await p.activate_hooks()
        await p.mouse_handler.activate_mouseless()
        await p.send_key(Keycode.PAGE_DOWN, 0.1)
        await p.use_potion_if_needed(health_percent=20, mana_percent=5)

    Total_Count = 0
    total = time()
    while True:
        start = time()

        await asyncio.gather(*[decide_heal(p) for p in clients]) 

        # Entering Dungeon
        print("Entering sigil")
        for p in clients:
          while await p.is_in_npc_range():
            await asyncio.sleep(0.4)
            await p.send_key(Keycode.X, 0.1)
        await asyncio.gather(*[p.wait_for_zone_change() for p in clients])
        await asyncio.sleep(1.4)

        # Initial battle starter
        print("[p1] Teleporting to mob")
        await p1.tp_to_closest_mob()
        await asyncio.sleep(0.3)
        await p1.send_key(Keycode.W, 0.1)
        await p1.send_key(Keycode.D, 0.1)
        await asyncio.sleep(0.4)
        for p in clients[1:]:
            print(f"[{p.title}] Teleporting to p1")
            p1pos = await p1.body.position()
            await p.teleport(p1pos)
            await asyncio.sleep(0.3)
            await p.send_key(Keycode.W, 0.1)
            await p.send_key(Keycode.D, 0.1)
            await asyncio.sleep(0.2)

        # Battle:
        print("Preparing combat configs")
        combat_handlers = []
        for p in clients: # Setting up the parsed configs to combat_handlers
            file_path = pathlib.Path(__file__).parent / "configs" / f"{p.title}spellconfig.txt"
            combat_handlers.append(SprintyCombat(p, CombatConfigProvider(str(file_path.absolute()), cast_time=1)))
        print("Starting combat")
        await asyncio.gather(*[h.wait_for_combat() for h in combat_handlers]) # Battle
        print("Combat ended")
        await asyncio.sleep(7)
        for p in clients:
          await p.send_key(Keycode.W, 0.1)
          await logout_and_in(p)
          await asyncio.sleep(2)

        # Healing
        for p in clients:
          if await p.needs_potion(health_percent=20, mana_percent=5):
            print(f"[{p.title}] Needs potion, attempting to use")
            await p.use_potion_if_needed(health_percent=20, mana_percent=5)
          await asyncio.sleep(0.2)

        # Time
        Total_Count += 1
        print("The Total Amount of Runs: ", Total_Count)
        print("Time Taken for run: ", round((time() - start) / 60, 2), "minutes")
        print("Total time elapsed: ", round((time() - total) / 60, 2), "minutes")
        print("Average time per run: ", round(((time() - total) / 60) / Total_Count, 2), "minutes")


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