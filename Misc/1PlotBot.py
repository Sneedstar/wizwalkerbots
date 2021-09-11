import asyncio

from wizwalker.extensions.wizsprinter import WizSprinter

async def main(sprinter):    
    client = sprinter.get_new_clients()[0]
    await client.activate_hooks()
    await client.mouse_handler.activate_mouseless()
    await client.mouse_handler.click(400, 300)

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