import asyncio
from time import time

from wizwalker.constants import Keycode
from wizwalker.extensions.wizsprinter.WizSprinter import WizSprinter


potion_ui_buy = [
    "fillallpotions",
    "buyAction",
    "btnShopPotions",
    "centerButton",
    "fillonepotion",
    "buyAction",
    "exit"
]

class healthAndManaCheck(WizSprinter):
    async def auto_buy_potions(self):
        # Head to home world gate
        await asyncio.sleep(0.1)
        await self.send_key(Keycode.HOME, 0.1)
        await self.wait_for_zone_change()
        while not await self.is_in_npc_range():
            await self.send_key(Keycode.S, 0.1)
        await self.send_key(Keycode.X, 0.1)
        await asyncio.sleep(1.2)
        # Go to Wizard City
        await self.mouse_handler.click_window_with_name('wbtnWizardCity')
        await asyncio.sleep(0.15)
        await self.mouse_handler.click_window_with_name('teleportButton')
        await self.wait_for_zone_change()
        # Walk to potion vendor
        await self.goto(-0.5264079570770264, -3021.25244140625)
        await self.send_key(Keycode.W, 0.5)
        await self.wait_for_zone_change()
        await self.goto(11.836355209350586, -1816.455078125)
        await self.send_key(Keycode.W, 0.5)
        await self.wait_for_zone_change()
        await self.goto(-880.2447509765625, 747.2051391601562)
        await self.goto(-4272.06884765625, 1251.950927734375)
        await asyncio.sleep(0.3)
        if not await self.is_in_npc_range():
            await self.teleport(-4442.06005859375, 1001.5532836914062)
        await self.send_key(Keycode.X, 0.1)
        await asyncio.sleep(0.2)
        # Buy potions
        for i in potion_ui_buy:
            await self.mouse_handler.click_window_with_name(i)
            await asyncio.sleep(0.1)
        # Return
        await self.send_key(Keycode.PAGE_UP, 0.1)
        await self.wait_for_zone_change()
        await self.send_key(Keycode.PAGE_DOWN, 0.1)

    async def collect_wisps(self):
        # Head to home world gate
        await self.send_key(Keycode.HOME, 0.1)
        await self.wait_for_zone_change()
        while not await self.is_in_npc_range():
            await self.send_key(Keycode.S, 0.1)
        await self.send_key(Keycode.X, 0.1)
        await asyncio.sleep(0.5)
        # Go to Mirage
        for i in range(3):
            await self.mouse_handler.click_window_with_name('rightButton')
        await asyncio.sleep(0.1)
        await self.mouse_handler.click_window_with_name('wbtnMirage')
        await asyncio.sleep(0.1)
        await self.mouse_handler.click_window_with_name('teleportButton')
        await self.wait_for_zone_change()
        # Collecting wisps
        while await self.stats.current_hitpoints() < await self.stats.max_hitpoints():
            await self.tp_to_closest_health_wisp()
            await asyncio.sleep(0.1)
        while await self.stats.current_mana() < await self.stats.max_mana():
            await self.tp_to_closest_mana_wisp()
            await asyncio.sleep(0.1)
        # Return
        await self.send_key(Keycode.PAGE_UP, 0.2)
        await self.wait_for_zone_change()
        await self.send_key(Keycode.PAGE_DOWN, 0.2)

    async def decide_heal(self):
        if await self.needs_potion(health_percent=5, mana_percent=5):
            if await self.stats.current_gold() >= 30000: 
                print(f"[{self.title}] Buying Potions")
                await self.auto_buy_potions()
            else:
                print(f"[{self.title}] Collecting Wisps")
                await self.collect_wisps()