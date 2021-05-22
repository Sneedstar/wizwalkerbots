import asyncio
from time import time

from wizwalker.constants import Keycode
from wizwalker.extensions.wizsprinter import SprintyCombat, CombatConfigProvider, WizSprinter
from healthAndManaCheck import healthAndManaCheck

async def main(sprinter):
    potion = healthAndManaCheck()
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

    combat_handlers = []
    Total_Count = 0
    total = time()
    while True:
        start = time()

        # Initial battle starter
        await p1.tp_to_closest_mob()
        await p1.send_key(Keycode.W, 0.1)
        await asyncio.sleep(0.4)
        for p in clients[1:]:
            p1pos = await p1.body.position()
            await p.teleport(p1pos)
            await p.send_key(Keycode.W, 0.1)
            await asyncio.sleep(0.2)

        # Battle:
        print("Initiating combat")
        for p in clients: # Setting up the parsed configs to combat_handlers
            combat_handlers.append(SprintyCombat(p, CombatConfigProvider(f'configs/{p.title}spellconfig.txt', cast_time=0.5, memory_timeout= 5.0)))
        await asyncio.gather(*[h.wait_for_combat() for h in combat_handlers]) # .wait_for_combat() to wait for combat to then go through the battles
        print("Combat ended")

        # Unghosting
        await asyncio.sleep(0.4)
        await asyncio.gather(*[p.send_key(Keycode.S, 0.1) for p in clients])
        await asyncio.gather(*[p.send_key(Keycode.W, 0.1) for p in clients])
        
        # Healing
        await asyncio.gather(*[p.use_potion_if_needed(health_percent=5, mana_percent=5) for p in clients]) # WizSprinter function now, not WizSDK
        await asyncio.gather(*[healthAndManaCheck.decide_heal(p) for p in clients])
        await asyncio.sleep(5)

        # Time
        Total_Count += 1
        print("The Total Amount of Runs: ", Total_Count)
        print("Time Taken for run: ", round((time() - start) / 60), "minutes")
        print("Total time elapsed: ", round((time() - total) / 60), "minutes")
        print("Average time per run: ", round(((time() - total) / 60) / Total_Count), "minutes")


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