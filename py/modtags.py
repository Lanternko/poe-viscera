"""Tag each viscera by what its mods do, for the mod filter menu.
TAGS: (group, key, zh, en, line regex). A line can carry several tags.
Offence/defence words are told apart by DEF: a line about damage you take,
your resistances or ailments on you is never an offensive damage-type line."""
import re

DEF = re.compile(r"taken|on you|you take|Avoid|Unaffected|inflicted on you|Immune|Cannot be|cannot be|Attackers|"
                 r"to (?:maximum |all maximum )?(?:\w+ )?Resistances?$|Resistances equal", re.I)
ENEMY = re.compile(r"Enem|Monster|Minion|Zombie|Corpse|Undead|Skeleton|Cost Life", re.I)
TAGS = [
 ("dmg", "phys", "物理", "Physical", r"Physical|Bleed|Impale"),
 ("dmg", "fire", "火焰", "Fire", r"Fire|Ignite|Burning|Scorch"),
 ("dmg", "cold", "冰冷", "Cold", r"Cold|Chill|Freeze|Frostbite"),
 ("dmg", "light", "閃電", "Lightning", r"Lightning|Shock|Conductivity"),
 ("dmg", "chaos", "混沌", "Chaos", r"Chaos|Poison|Wither"),
 ("dmg", "elem", "隨機元素", "Random element", r"random Element|Random Element"),
 ("dmg", "any", "通用傷害", "Generic damage", r"(?:increased|more) Damage|Double Damage|Enemies take"),
 ("def", "life", "生命", "Life", r"\bLife\b"),
 ("def", "mana", "魔力", "Mana", r"\bMana\b"),
 ("def", "es", "能量護盾", "Energy Shield", r"Energy Shield"),
 ("def", "armour", "護甲", "Armour", r"Armour"),
 ("def", "eva", "閃避", "Evasion", r"Evasion|Phasing|Elusive"),
 ("def", "res", "抗性", "Resistance", r"Resistance"),
 ("def", "pdr", "物理減免", "Phys. reduction", r"Physical Damage Reduction|Physical Damage taken|Physical Damage from Hits|Defend with|Fortification|Avoid Physical|Physical Damage over Time taken"),
 ("def", "block", "格擋", "Block", r"\bBlock"),
 ("def", "supp", "法術壓制", "Suppression", r"Suppress"),
 ("def", "dtaken", "元素／混沌減傷", "Ele / chaos damage taken", r"(?:Fire|Cold|Lightning|Chaos|Burning|Elemental) Damage taken|(?:Fire|Cold|Lightning) Damage from Hits taken as|Damage taken as"),
 ("def", "ail", "異常／暈眩防護", "Ailment / stun immunity", r"."),
 ("misc", "minion", "召喚物", "Minions", r"Minion|Zombie|Skeleton|Spectre|Wisp|Spiders|Void Spawn"),
 ("misc", "crit", "暴擊", "Critical", r"Critical"),
 ("misc", "speed", "速度", "Speed", r"Speed|Cooldown Recovery"),
 ("misc", "proj", "投射物", "Projectiles", r"Projectile|Arrow|Pierce|Fork|Chain"),
 ("misc", "aoe", "範圍", "Area", r"Area of Effect|Radius of"),
 ("misc", "curse", "詛咒", "Curses", r"Curse"),
 ("misc", "charge", "充能／怒氣", "Charges / Rage", r"Charge|Rage"),
 ("misc", "corpse", "屍體", "Corpses", r"[Cc]orpse"),
 ("misc", "stun", "暈眩敵人", "Stun", r"Stun"),
 ("misc", "skill", "給予技能", "Grants skill", r"Grants Level|Trigger Level|Transfiguration|grant level|Shared Suffering"),
 ("misc", "attr", "屬性", "Attributes", r"Strength|Dexterity|Intelligence|Attribute"),
 ("misc", "gem", "寶石等級／品質", "Gem level / quality", r"Level of all|Quality of all"),
 ("misc", "buff", "旗幟／獻祭／圖騰／戰吼", "Banner / Offering / Totem / Warcry", r"Banner|Offering|Consecrated|Totem|Warcry"),
 ("misc", "blind", "致盲", "Blind", r"Blind"),
 ("misc", "loot", "掉落", "Loot", r"Gold|Coin|Scroll|drop"),
 ("misc", "other", "其他", "Other", r"(?!)"),
]
_RX = [(k, re.compile(rx)) for _, k, _, _, rx in TAGS]
AIL = re.compile(r"Avoid (?:being Stunned|Bleeding|Elemental Ailments)|avoid Corrupted|Unaffected|cannot be inflicted on you|"
                 r"Cannot be|cannot be Stunned|Immune|Effect of (?:Chill|Curses) on you|Duration on you|expires .* faster|Stun Threshold|Stun and Block Recovery|doesn't cause you", re.I)


def tags(lines):
    out = set()
    for line in lines:
        d = bool(DEF.search(line))
        for k, rx in _RX:
            if k == "ail":
                if AIL.search(line) and "Enemy Stun" not in line:
                    out.add(k)
                continue
            if not rx.search(line):
                continue
            grp = next(g for g, kk, *_ in TAGS if kk == k)
            if grp == "dmg" and d:
                continue  # damage you take / your resists are defence, not damage type
            if k == "any" and (d and "Enemies take" not in line or re.search(r"Physical|Fire|Cold|Lightning|Chaos|Elemental|Spell|Minion|Projectile|Zombie|Skeleton", line)):
                continue
            if k == "life" and ENEMY.search(line):
                continue
            if k == "stun" and (d or "Threshold" in line and "Enemy" not in line or "Block Recovery" in line):
                continue
            if k in ("block",) and ("Enemy Chance" in line or "Block Recovery" in line or "Blocked" in line):
                continue
            if k == "res" and ("Penetrates" in line or "Enemy" in line or "Exposure" in line):
                continue
            if k == "pdr" and "Enemy" in line:
                continue
            out.add(k)
    return sorted(out) or ['other']
