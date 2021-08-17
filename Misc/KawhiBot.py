import asyncio

from wizwalker import XYZ
from wizwalker.constants import Keycode, user32
from wizwalker.extensions.wizsprinter import WizSprinter

async def main(sprinter):
    client = sprinter.get_new_clients()[0]
    await client.activate_hooks()
    await client.mouse_handler.activate_mouseless()
    client.title = "KawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBotKawhiBot"
    pos = await client.body.position()
    for i in range(40):
        await client.send_key(Keycode.W)
        await client.teleport(XYZ(pos.x, pos.y, 2000))
        print("KawhiBot")
    await client.send_key(Keycode.ESC)
    await asyncio.sleep(0.4)
    await client.mouse_handler.click_window_with_name('QuitButton')
    await asyncio.sleep(5.5)
    await client.mouse_handler.click_window_with_name('btnExit')

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