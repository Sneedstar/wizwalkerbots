import asyncio
from typing import List, Optional

import wizwalker
from wizwalker.combat import CombatHandler, CombatMember, CombatCard
from wizwalker.memory.memory_objects.spell_effect import EffectTarget

async def get_spells_by_type_name(client, type_name: str) -> list[wizwalker.combat.CombatCard]:
  async def _pred(card):
    return (await card.type_name()).lower() == type_name and await card.is_castable()

  return await client.get_cards_with_predicate(_pred)

# From WizSprinter by SirOlaf; changed from .name to .display_name
async def get_card_vaguely_named(client, name: str) -> Optional[CombatCard]:
  async def _pred(card: CombatCard):
    return name.lower() in (await card.display_name()).lower()

  return await client.get_cards_with_predicate(_pred)

async def highest_pip_spell(spells):
  card_pip = 0
  for spell in spells:
    graphical_spell = await spell.wait_for_graphical_spell()
    rank_struct = await graphical_spell.rank()
    rank = rank_struct.regular_rank
    if rank >= card_pip:
      card_pip = rank
      to_cast = spell

  return to_cast

async def already_enchanted(spells):
  enchanteds = []
  for spell in spells:
    if await spell.is_enchanted():
      enchanteds.append(spell)

  return enchanteds

async def get_school_template_name(self, member: CombatMember):
    part = await member.get_participant()
    school_id = await part.primary_magic_school_id()
    return await self.client.cache_handler.get_template_name(school_id)

class LowLevelCombat(CombatHandler):
  async def handle_round(self):
    await asyncio.sleep(0.5)

    mobs = await self.get_all_monster_members()
    client_member = await self.get_client_member()

    # Finds lowest health mob
    to_kill_health = 2000000
    for mob in mobs:
      if await mob.health() < to_kill_health:
        to_kill_health = await mob.health()
        to_kill = mob

    # Heals
    if await client_member.health() < 200 and (heals := await get_spells_by_type_name(self, "heal")):
      print("Casting heal")
      await heals[0].cast(client_member)
      return

    # Damages
    if damages := await get_spells_by_type_name(self, "damage"):
      # Find highest accuracy spell
      acc = 0
      for spell in damages:
        if await spell.accuracy() >= acc:
          acc = await spell.accuracy()
          to_cast = spell

      await to_cast.cast(to_kill)
      return

    print("No available spells, passing")
    await self.pass_button()

class HighLevelCombat(CombatHandler):
  async def handle_round(self):
    await asyncio.sleep(0.5)

    client_member = await self.get_client_member()
    final_cast = "empty"
    target = "empty"
    mobs = await self.get_all_monster_members()
    
    # Finds the boss(es)
    is_boss = False
    is_multi_boss = False
    for mob in mobs:
      if await mob.is_boss():
        if is_boss == True:
          is_multi_boss = True
        is_boss = True
        boss = mob
    if is_multi_boss:
      is_boss = False

    # Finds highest health mob
    to_kill_health = 0
    for mob in mobs:
      if await mob.health() > to_kill_health:
        to_kill_health = await mob.health()
        to_kill = mob

    # Heals
    if ((await client_member.health() / await client_member.max_health()) < 1.1) and (heals := await get_spells_by_type_name(self, "heal")):
      await asyncio.sleep(0.3)
      # Checking for already enchanted spells
      enchanted_heals = await already_enchanted(heals)
      if enchanted_heals:
        to_cast = enchanted_heals[0]
      else:
        to_cast = heals[0]
      # Enchanting
      if (heal_enchants := (await get_card_vaguely_named(self, "primordial") or await get_card_vaguely_named(self, "radical"))) and (not enchanted_heals) and (not await to_cast.is_item_card()):
        print(f"Enchanting {await to_cast.display_name()} with {await heal_enchants[0].display_name()}")
        await heal_enchants[0].cast(to_cast)
        await asyncio.sleep(0.2)
        enchanted_heals = await already_enchanted(await get_spells_by_type_name(self, "heal"))
        to_cast = enchanted_heals[0]
      await asyncio.sleep(0.3)
      final_cast = to_cast
    
    # Prisms
    if (is_boss) and (final_cast == "empty"):
      if (await get_school_template_name(self, boss) == await get_school_template_name(self, client_member)) and (prisms := await get_card_vaguely_named(self, "prism")):
        await asyncio.sleep(0.3)
        final_cast = prisms[0]

    # Charms
    if (charms := await get_spells_by_type_name(self, "charm")) and (final_cast == "empty"):
      await asyncio.sleep(0.3)
      # Checking for already enchanted spells
      enchanted_charms = await already_enchanted(charms)
      if enchanted_charms:
        to_cast = enchanted_charms[0]
      else:
        to_cast = charms[0]
      # Enchanting
      if (sharps := await get_card_vaguely_named(self, "sharpened")) and (not enchanted_charms) and (not await to_cast.is_item_card()):
        print(f"Enchanting {await to_cast.display_name()} with {await sharps[0].display_name()}")
        await sharps[0].cast(to_cast)
        await asyncio.sleep(0.2)
        enchanted_charms = await already_enchanted(await get_spells_by_type_name(self, "charm"))
        to_cast = enchanted_charms[0]
      await asyncio.sleep(0.3)
      final_cast = to_cast

    # Wards
    if (wards := await get_spells_by_type_name(self, "ward")) and (is_boss) and (final_cast == "empty"):
      await asyncio.sleep(0.3)
      # Checking for already enchanted spells
      enchanted_wards = await already_enchanted(wards)
      if enchanted_wards:
        to_cast = enchanted_wards[0]
      else:
        to_cast = wards[0]
      # Enchanting
      if (potents := await get_card_vaguely_named(self, "potent")) and (not enchanted_wards) and (not await to_cast.is_item_card()):
        print(f"Enchanting {await to_cast.display_name()} with {await potents[0].display_name()}")
        await potents[0].cast(to_cast)
        await asyncio.sleep(0.2)
        enchanted_wards = await already_enchanted(await get_spells_by_type_name(self, "ward"))
        to_cast = enchanted_wards[0]
      await asyncio.sleep(0.3)
      final_cast = to_cast

    # Auras
    if (auras := await get_spells_by_type_name(self, "aura")) and (final_cast == "empty"):
      await asyncio.sleep(0.5)
      final_cast = auras[0]

    # Globals
    if (globals := await get_spells_by_type_name(self, "global")) and (final_cast == "empty"):
      await asyncio.sleep(0.5)
      final_cast = globals[0]

    # Damages
    if (await get_spells_by_type_name(self, "damage") or await get_spells_by_type_name(self, "steal") or await get_spells_by_type_name(self, "aoe")) and (final_cast == "empty"):
      await asyncio.sleep(0.3)
      damages = await get_spells_by_type_name(self, "damage") + await get_spells_by_type_name(self, "steal") + await get_spells_by_type_name(self, "aoe")
      # Checking for already enchanted spells
      enchanted_damages = await already_enchanted(damages)
      if enchanted_damages:
        to_cast = await highest_pip_spell(enchanted_damages)
      else:
        to_cast = await highest_pip_spell(damages)
      # Enchanting
      if (damage_enchants := await self.get_damage_enchants()) and (not enchanted_damages) and (not await to_cast.is_item_card()):
        print(f"Enchanting {await to_cast.display_name()} with {await damage_enchants[0].display_name()}")
        await damage_enchants[0].cast(to_cast)
        await asyncio.sleep(0.2)
        enchanted_damages = await already_enchanted(await get_spells_by_type_name(self, "damage"))
        to_cast = enchanted_damages[0]
      await asyncio.sleep(0.3)
      final_cast = to_cast

    # Targeting
    target_effects = []
    effects = await final_cast.get_spell_effects()
    for effect in effects:
      target_effects.append(await effect.effect_target())

    for target_effect in target_effects:
      if target_effect is EffectTarget.target_global or EffectTarget.self or EffectTarget.enemy_team or EffectTarget.friendly_team:
        target = None
    for target_effect in target_effects:
      if (target_effect is EffectTarget.enemy_single) and ((await final_cast.type_name() == "Ward") or ("prism" in await final_cast.display_name())) and (is_boss):
        target = boss
    for target_effect in target_effects:
      if target_effect is EffectTarget.friendly_single:
        target = client_member
    for target_effect in target_effects:
      if target_effect is EffectTarget.enemy_single:
        target = to_kill

    # Casting
    if final_cast:
      if target != None:
        print(f"Casting {await final_cast.display_name()} at {await target.name()}")
      else:
        print(f"Casting {await final_cast.display_name()}")
      await final_cast.cast(target)
    else:
      print("No available spells, passing")
      await self.pass_button()
    await self.client.mouse_handler.deactivate_mouseless()
    return