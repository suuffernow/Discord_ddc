import random, asyncio
import messageSend

class fighter:
    def __init__(self, name="test", atk=1, hp=2, dex_Atk=0, dex_Def = 0):
        self.name = name
        self.atk = atk
        self.hp = hp
        self.dex_Atk = dex_Atk
        self.dex_Def = dex_Def

    def attack(self):
        rng = random.randint(1, 1000)
        if (rng + self.dex_Atk - self.dex_Def < 0):
            multiplier = 0
        elif (rng + self.dex_Atk - self.dex_Def > 1500):
            multiplier = 1500
        else:
            multiplier = rng + self.dex_Atk - self.dex_Def
        multiplier = multiplier / 1000 + 0.5
        atk_amt = self.atk * multiplier
        return round(atk_amt,1)

class combat:
    async def start_fight(self, fighter1, fighter2, message, message_string, ctx):
        print(f"{fighter1.name} vs {fighter2.name} - fight started")

        #loop through 2 player combat
        while True:
            result = await self.get_attack_result(fighter1, fighter2, message_string)
            print(f"{fighter1.name} attacked")
            message_string = result[2]
            await messageSend.postMessage(ctx, message_string, "Combat2", message)
            #if P2 HP reaches 0, break loop
            if result[0] == True:
                return result[1]
            result = await self.get_attack_result(fighter2, fighter1, message_string)
            print(f"{fighter2.name} attacked")
            message_string = result[2]
            await messageSend.postMessage(ctx, message_string, "Combat2", message)
            # if P1 HP reaches 0, break loop
            if result[0] == True:
                return result[1]

    async def get_attack_result(self, fighterA, fighterB, message_string):
        fighterA_atk = fighterA.attack()
        fighterB.hp = fighterB.hp - fighterA_atk
        combat_log = f"\n**{fighterA.name}** attacks **{fighterB.name}** and deals {fighterA_atk} damage\n{fighterB.name} is down to {round(fighterB.hp,2)} health"
        if fighterB.hp <=0:
            await asyncio.sleep(1)
            message_string += f"\n{combat_log}\n\n{fighterB.name} has been defeated!"
            return True, fighterA.name, message_string

        else:
            await asyncio.sleep(1)
            message_string += f"\n{combat_log}"
            return False, fighterB.name, message_string