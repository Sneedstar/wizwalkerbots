# wizwalker-bots
Simple repo to house my WizWalker bots. Everything you need to know is in the README. Please do not try to dm me. <br />
Don't make messages in #support about my bots until you read the entire README. It's called README for a reason. If you cannot read, I'm sure I can find someone to read it to you.

Note: you need a house with a world gate behind you equipped

## Running from releases
1. Download from [here](https://github.com/MajorPain1/wizwalkerbots/releases) <br />
2. Extract the zip <br />
3. Double click the exe in the desired location you want to run the script <br />

## Running from source
Run `pip install -r requirements.txt` to install required libraries <br />
To run from source do `py -m {name of bot}` in the main github folder <br />

Most people should run from releases. Just extract the zip, set your configs, and run the exe.

# WizFighter
WizFighter looks through your hand and decides what card to use. It's priority goes as follows (keep in mind it will prefer to cast enchanted spells): <br />
Heals (if low on health), Prisms (if boss and if boss is your school), charms, wards (if boss), auras, globals, AOEs, damage spells, passing
