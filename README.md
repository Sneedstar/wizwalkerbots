# Major's WizWalker Bots
Simple repo to house my WizWalker bots. Everything you need to know is in the README. Please do not try to DM me. <br />
Don't make messages in #bot-support about my bots until you read the entire README. It's called README for a reason. If you cannot read, I'm sure I can find someone to read it to you.

Note: you need a house with a world gate behind you equipped

## Running from releases
DO NOT RUN FROM RELEASES BECAUSE PYINSTALLER IS NOT UPDATED TO 3.10
1. Download from [here](https://github.com/MajorPain1/wizwalkerbots/releases) <br />
2. Double click the exe in the desired location you want to run the script <br />

## Running from source
1. Install python 3.10 [here](https://www.python.org/downloads/release/python-3100/) and click the checkmark to add to PATH when you are installing it <br />
2. Make sure you are on the `main` branch of this github. Not any other tags. You can select the `main` branch with the drop down box (box with a down arrow) in the top left by the word that says `branch`. 
3. Install it as a ZIP with the big green button on the top right <br />
4. Open cmd in the main github folder. Make sure it is called `wizwalkerbots-main`. You can achieve this by typing `cmd` in the top address bar in the file explorer. The next commands will be in this cmd <br />
5. Run `pip install -r requirements.txt` to install required libraries <br />
6. Run `py -m name_of_folder_of_the_bot` when you are ready to start the bot. Example: `py -m UniversalBot` <br />

Most people should run from releases unless specified otherwise.

# WizFighter
WizFighter looks through your hand and decides what card to use. It's priority goes as follows (keep in mind it will prefer to cast enchanted spells): <br />
1. Heals (if low on health)
2. Prisms (if boss and if boss is your school)
3. Damage Positive Charms
4. Positive Wards
5. Damage Auras & Globals
6. Other Positive Charms
7. AOE Damage Spells
8. Other Damage Spells
9. Negative Charms
10. Negative Wards (shields)
11. Other Auras & Globals
12. Passing <br />
