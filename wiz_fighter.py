import asyncio

from wizwalker.memory.memory_objects import game_stats
from wizwalker.combat import CombatHandler, CombatMember
from wizwalker.memory.memory_objects.enums import SpellEffects, EffectTarget

# TODO: Damage Calculations
# TODO: Team Logic

DAMAGE_EFFECTS = [
  SpellEffects.damage,
  SpellEffects.damage_no_crit,
  SpellEffects.damage_over_time,
  SpellEffects.damage_per_total_pip_power,
  SpellEffects.max_health_damage,
  SpellEffects.steal_health
]
DAMAGE_TARGETS = [
  EffectTarget.enemy_team_all_at_once, 
  EffectTarget.enemy_single, 
  EffectTarget.enemy_team
]
DAMAGE_ENCHANT_EFFECTS = [
  SpellEffects.modify_card_damage,
  SpellEffects.modify_card_accuracy,
  SpellEffects.modify_card_armor_piercing, 
  SpellEffects.modify_card_damage_by_rank
]
STRICT_DAMAGE_ENCHANT_EFFECTS = [
  SpellEffects.modify_card_damage,
  SpellEffects.modify_card_damage_by_rank
]
HEALING_EFFECTS = [
  SpellEffects.heal,
  SpellEffects.heal_over_time,
  SpellEffects.heal_percent,
  SpellEffects.heal_by_ward,
  SpellEffects.max_health_heal
]
TRAP_ENCHANT_EFFECTS = [
  SpellEffects.modify_card_incoming_damage, 
  SpellEffects.protect_card_harmful
]
CHARM_ENCHANT_EFFECTS = [
  SpellEffects.modify_card_outgoing_damage, 
  SpellEffects.protect_card_beneficial
]
FRIENDLY_TARGETS = [
  EffectTarget.friendly_single, 
  EffectTarget.friendly_team, 
  EffectTarget.friendly_team_all_at_once
]
ENEMY_TARGETS = [
  EffectTarget.enemy_single, 
  EffectTarget.enemy_team, 
  EffectTarget.enemy_team_all_at_once
]
DAMAGE_AURA_GLOBAL_EFFECTS = [
  SpellEffects.modify_outgoing_damage, 
  SpellEffects.modify_outgoing_armor_piercing
]
AURA_GLOBAL_TARGETS = [
  EffectTarget.self, 
  EffectTarget.target_global
]
AURA_GLOBAL_EFFECTS = [
  SpellEffects.pip_conversion, 
  SpellEffects.power_pip_conversion, 
  SpellEffects.modify_power_pip_chance, 
  SpellEffects.modify_outgoing_armor_piercing, 
  SpellEffects.modify_outgoing_heal, 
  SpellEffects.modify_accuracy
]
CHARM_EFFECTS = [
  SpellEffects.modify_outgoing_damage,
  SpellEffects.modify_accuracy,
  SpellEffects.dispel
]
NONE_TARGETS = [
  EffectTarget.self, 
  EffectTarget.enemy_team, 
  EffectTarget.enemy_team_all_at_once, 
  EffectTarget.target_global, 
  EffectTarget.friendly_team, 
  EffectTarget.friendly_team_all_at_once
]
DAMAGE_AOE_TARGETS = [
  EffectTarget.enemy_team,
  EffectTarget.enemy_team_all_at_once
]

class WizFighter(CombatHandler):
  async def get_school_template_name(self, member: CombatMember):
    part = await member.get_participant()
    school_id = await part.primary_magic_school_id()
    return await self.client.cache_handler.get_template_name(school_id)

  async def read_target_effect(self, card):
    card_targets = []

    for effect in await card.get_spell_effects():
      type_name = await effect.maybe_read_type_name()

      if "random" in type_name.lower() or "variable" in type_name.lower():
        subeffects = await effect.maybe_effect_list()
        card_targets.append(await subeffects[0].effect_target())

      else:
        card_targets.append(await effect.effect_target())

    return card_targets

  async def read_spell_effect(self, card):
    spell_effects = []

    for effect in await card.get_spell_effects():
      type_name = await effect.maybe_read_type_name()

      if "random" in type_name.lower() or "variable" in type_name.lower():
        subeffects = await effect.maybe_effect_list()
        spell_effects.append(await subeffects[0].effect_type())

      else:
        spell_effects.append(await effect.effect_type())

    return spell_effects

  async def read_effect_param(self, card):
    effect_params = []

    for effect in await card.get_spell_effects():
      type_name = await effect.maybe_read_type_name()

      if "random" in type_name.lower() or "variable" in type_name.lower():
        subeffects = await effect.maybe_effect_list()

        for subeffect in subeffects:
          effect_params.append(await subeffect.effect_param())

      else:
        effect_params.append(await effect.effect_param())

    return effect_params

  async def average_effect_param(self, card):
    effect_params = []

    for effect in await card.get_spell_effects():
      type_name = await effect.maybe_read_type_name()

      if "random" in type_name.lower() or "variable" in type_name.lower():
        subeffects = await effect.maybe_effect_list()

        for subeffect in subeffects:
          effect_params.append(await subeffect.effect_param())
        
        if effect_params:
          total = 0
          for effect_param in effect_params:
            total += effect_param
        
          return (total / len(effect_params))

      else:
        return await effect.effect_param()

  async def highest_health_mob(self, mobs):
    to_kill_health = 0

    for mob in mobs:
      if await mob.health() > to_kill_health:
        to_kill_health = await mob.health()
        to_kill = mob
      
    return to_kill 

  async def highest_damage_card(self, cards: list):
    highest_damage = 0
    damagest_card = "empty"

    for card in cards:

      card_effects = await self.read_spell_effect(card)
      card_targets = await self.read_target_effect(card)

      if (any(effects in card_effects for effects in DAMAGE_EFFECTS)) and (any(effects in card_targets for effects in DAMAGE_TARGETS)):
        if await self.average_effect_param(card) > highest_damage:
          highest_damage = await self.average_effect_param(card)
            
          damagest_card = card

    return damagest_card

  async def highest_damage_aoe(self, cards: list):
    highest_damage = 0
    damagest_aoe = "empty"

    for card in cards:

      card_effects = await self.read_spell_effect(card)
      card_targets = await self.read_target_effect(card)

      if (any(effects in card_effects for effects in DAMAGE_EFFECTS)) and (any(effects in card_targets for effects in DAMAGE_AOE_TARGETS)):
        if await self.average_effect_param(card) > highest_damage:
          highest_damage = await self.average_effect_param(card)
            
          damagest_aoe = card

    return damagest_aoe

  async def get_enchanted_spells_by_spell_effect(self, effects: list):
    async def _pred(card):
      card_effects = await self.read_spell_effect(card)
      return (any(effect in card_effects for effect in effects)) and await card.is_castable() and await card.is_enchanted()

    return await self.get_cards_with_predicate(_pred)

  async def get_enchanted_spells_by_target_effect(self, effects: list):
    async def _pred(card):
      card_targets = await self.read_target_effect(card)
      return (any(effect in card_targets for effect in effects)) and await card.is_castable() and await card.is_enchanted()

    return await self.get_cards_with_predicate(_pred)

  async def handle_round(self):
    await asyncio.sleep(0.5)

    client_member = await self.get_client_member()
    mobs = await self.get_all_monster_members()
    to_kill = await self.highest_health_mob(mobs)
    
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

    # Sorting Enchants and Normals
    enchants = []
    normals = []
    for card in await self.get_cards():
      if await card.is_castable():
        enchant_target = await self.read_target_effect(card)

        if EffectTarget.spell in enchant_target:
          enchants.append(card)
        else:
          normals.append(card)

    # Sorting enchants
    heal_enchants = []   
    damage_enchants = []
    strict_damage_enchants = []
    trap_enchants = [] 
    charm_enchants = []
    for enchant in enchants:
      enchant_types = await self.read_spell_effect(enchant)

      if SpellEffects.modify_card_heal in enchant_types:
        heal_enchants.append(enchant)
      if any(effects in enchant_types for effects in DAMAGE_ENCHANT_EFFECTS):
        damage_enchants.append(enchant)
      if any(effects in enchant_types for effects in STRICT_DAMAGE_ENCHANT_EFFECTS):
        strict_damage_enchants.append(enchant)
      if any(effects in enchant_types for effects in TRAP_ENCHANT_EFFECTS):
        trap_enchants.append(enchant)
      if any(effects in enchant_types for effects in CHARM_ENCHANT_EFFECTS):
        charm_enchants.append(enchant)

    # Finding Highest Damage card
    damagest_card = await self.highest_damage_card(normals)
    damagest_aoe = await self.highest_damage_aoe(normals)

    ## Find card to cast
    final_cast = None
    card_value = 0
    for card in normals:

      # Spell Effects (I hate them)
      effect_types = await self.read_spell_effect(card)
      effect_targets = await self.read_target_effect(card)

      # Heals
      if (any(effects in effect_types for effects in HEALING_EFFECTS)) and ((await client_member.health() / await client_member.max_health()) < 0.15):
        await asyncio.sleep(0.3)
        card_value = 11
        final_cast = card

      # Prisms
      if (is_boss) and (card_value < 10):
        if (SpellEffects.modify_incoming_damage_type in effect_types) and (await self.get_school_template_name(boss) == await self.get_school_template_name(client_member)):
          await asyncio.sleep(0.3)
          card_value = 10
          final_cast = card

      # Damage Positive Charms
      if (SpellEffects.modify_outgoing_damage in effect_types) and (any(effects in effect_targets for effects in FRIENDLY_TARGETS)) and (card_value < 9):
        await asyncio.sleep(0.3)
        card_value = 9
        final_cast = card

      # Positive Wards
      if (SpellEffects.modify_incoming_damage in effect_types) and (any(effects in effect_targets for effects in ENEMY_TARGETS)) and (card_value < 8):
        await asyncio.sleep(0.3)
        card_value = 8
        final_cast = card

      # Damage Auras/Globals
      if (any(effects in effect_types for effects in DAMAGE_AURA_GLOBAL_EFFECTS)) and (any(effects in effect_targets for effects in AURA_GLOBAL_TARGETS)) and (card_value < 7):
        await asyncio.sleep(0.3)
        card_value = 7
        final_cast = card

      # Other Positive Charms
      if (any(effects in effect_types for effects in CHARM_EFFECTS)) and (any(effects in effect_targets for effects in FRIENDLY_TARGETS)) and (card_value < 6):
        await asyncio.sleep(0.3)
        card_value = 6
        final_cast = card

      # Damage AOEs
      if (any(effects in effect_types for effects in DAMAGE_EFFECTS)) and (any(effects in effect_targets for effects in DAMAGE_AOE_TARGETS)) and (card == damagest_aoe) and (card_value < 5):
        await asyncio.sleep(0.3)
        card_value = 5
        final_cast = card

      # Damage spells
      if (any(effects in effect_types for effects in DAMAGE_EFFECTS)) and (any(effects in effect_targets for effects in DAMAGE_TARGETS)) and (card == damagest_card) and (card_value < 4):
        await asyncio.sleep(0.3)
        card_value = 4
        final_cast = card
      
      # Negative Charms
      if (any(effects in effect_types for effects in CHARM_EFFECTS)) and (any(effects in effect_targets for effects in ENEMY_TARGETS)) and (card_value < 3):
        await asyncio.sleep(0.3)
        card_value = 3
        final_cast = card

      # Negative Wards
      if (SpellEffects.modify_incoming_damage in effect_types) and (any(effects in effect_targets for effects in FRIENDLY_TARGETS)) and (card_value < 2):
        await asyncio.sleep(0.3)
        card_value = 2
        final_cast = card

      # Other Auras/Globals
      if (any(effects in effect_types for effects in AURA_GLOBAL_EFFECTS)) and (any(effects in effect_targets for effects in AURA_GLOBAL_TARGETS)) and (card_value < 1):
        await asyncio.sleep(0.3)
        card_value = 1
        final_cast = card
    
    if final_cast:
      final_cast_types = await self.read_spell_effect(final_cast)
      final_cast_targets = await self.read_target_effect(final_cast)

      ## Enchanting
      if not await final_cast.is_item_card():

        # Heals
        if (any(effects in final_cast_types for effects in HEALING_EFFECTS)) and heal_enchants:
          print(f"Enchanting {await final_cast.display_name()} with {await heal_enchants[0].display_name()}")
          await heal_enchants[0].cast(final_cast)

          enchanted_cards = await self.get_enchanted_spells_by_spell_effect(HEALING_EFFECTS)
          final_cast = enchanted_cards[0]

        # Positive charms
        elif (SpellEffects.modify_outgoing_damage in final_cast_types) and (any(effects in final_cast_targets for effects in FRIENDLY_TARGETS)) and charm_enchants:
          print(f"Enchanting {await final_cast.display_name()} with {await charm_enchants[0].display_name()}")
          await charm_enchants[0].cast(final_cast)

          enchanted_cards = await self.get_enchanted_spells_by_spell_effect([SpellEffects.modify_outgoing_damage])
          final_cast = enchanted_cards[0]

        # Positive Wards
        elif (SpellEffects.modify_incoming_damage in final_cast_types) and (any(effects in final_cast_targets for effects in ENEMY_TARGETS)) and trap_enchants:
          print(f"Enchanting {await final_cast.display_name()} with {await trap_enchants[0].display_name()}")
          await trap_enchants[0].cast(final_cast)

          enchanted_cards = await self.get_enchanted_spells_by_spell_effect([SpellEffects.modify_incoming_damage])
          final_cast = enchanted_cards[0]

        # Damage
        elif (any(effects in final_cast_types for effects in DAMAGE_EFFECTS)) and (any(effects in final_cast_targets for effects in ENEMY_TARGETS)) and damage_enchants:
          print(f"Enchanting {await final_cast.display_name()} with {await damage_enchants[0].display_name()}")
          await damage_enchants[0].cast(final_cast)

          enchanted_cards = await self.get_enchanted_spells_by_spell_effect(DAMAGE_EFFECTS)
          final_cast = enchanted_cards[0]

      ## Targeting
      if EffectTarget.enemy_single in final_cast_targets:
        if is_boss:
          target = boss
        else:
          target = to_kill

      elif EffectTarget.friendly_single in final_cast_targets:
        target = client_member

      elif any(effects in final_cast_targets for effects in NONE_TARGETS):
        target = None

      # Casting
      if target != None:
        print(f"Casting {await final_cast.display_name()} at {await target.name()}")
      else:
        print(f"Casting {await final_cast.display_name()}")
      await final_cast.cast(target)

    else:
      print("No available spells, passing")
      await self.pass_button()

    return