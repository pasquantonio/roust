"""
Inspired by roundtable-lite seen in @gregermendles github fork originally by
czurch

Taking the professions and some class methods from that project I am going to
make a single player campaign.

This is my third attempt at making this. The first was a multiplayer game
attempt in NodeJS, the second was a single player terminal based game in
NodeJS.
I can't get passed the asynchronous aspect right now and just want to make it
so I am building a terminal based game in python.

Joe Pasquantonio
"""
import random
import time
import sqlite3

sqlite_file = "roust.sqlite"


class Entity(object):
    """
    Any general character, player or npc in game
    """
    def __init__(self, name, hp, atk, d, im, t):
        self.name = name
        self.max_health = hp
        self.health = hp
        self.attack = atk
        self.defense = d
        self.initiative = 0
        self.initMod = im
        self.alive = True
        self.type = t
        self.victories = 0

    def __str__(self):
        return "Name: {}\nClass: {}\nHealth: {}\n" \
               "Attack: {}\nDefense: {}\nInitiative: {}\n" \
               "InitMod: {}\n".format(self.name,
                                      self.type,
                                      self.health,
                                      self.attack,
                                      self.defense,
                                      self.initiative,
                                      self.initMod)

    def roll(self, sides=6):
        """
        Roll a dice
        """
        return random.randint(1, sides)

    def attackRoll(self):
        """
        attack + roll
        """
        return self.attack + self.roll()

    def initRoll(self):
        self.initiative = self.initiative + self.initMod + self.roll()

    def takeDamage(self, enemyAttack):
        damage = enemyAttack - self.defense
        if damage >= 0:
            log("{} takes {} damage".format(self.name, damage), "fight")
            self.health = self.health - damage
        else:
            log("{} takes no damage!".format(self.name), "fight")
        if self.health <= 0:
            self.alive = False
            self.health = 0

    def attackTurn(self, enemy):
        attackRoll = self.attackRoll()
        log("{}'s attack roll is {}".format(self.name, attackRoll), "fight")
        enemy.takeDamage(attackRoll)

    def revive(self):
        self.alive = True
        self.health = self.max_health


class Barbarian(Entity):
    """
    Barbarian

    On Attack Roll:
        roll two dice, if both rolls are the same, attack is doubled
    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Barbarian")

    def attackTurn(self, enemy):
        one = self.attackRoll()
        two = self.attackRoll()
        if one == two:
            log("{}'s attack roll is DOUBLED from {} to {}".format(self.name,
                                                                   one,
                                                                   one+two),
                                                                   "fight")
            enemy.takeDamage(one + two)
        else:
            log("{}'s attack roll is {}".format(self.name, one), "fight")
            enemy.takeDamage(one)


class Drunkard(Entity):
    """
    Drunkard

    On create:
        attack is increased by 2
        defense is decreased by 1

    rational:
        a drunkard's attacks are stronger but his defenses are lowered
    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Drunkard")
        self.attack += 2
        self.defense -= 1


class Knight(Entity):
    """
    Knight

    On create:
        attack is increased by 1
        defense is increased by 1
    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Knight")
        self.attack += 1
        self.defense += 1


class Priest(Entity):
    """
    Priest

    additional attributes:
        - spell_casts: tracks number of spells casted

    additional methods:
        - heal: heals a target by number rolled on dice
    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Priest")
        self.spell_casts = 0

    def heal(self, target):
        self.spells_casts += 1
        target.health += self.roll()


class Rogue(Entity):
    """
    Rogue

    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Rogue")
        self.initMod += 1
        self.mitigationSides = 4

    def mitigation(self):
        return self.roll(self.mitigationSides)

    def takeDamage(self, enemyAttack):
        mitigationRoll = self.mitigation()
        log("{}'s mitigation roll is {}".format(self.name,
                                                mitigationRoll),
                                                "fight")
        time.sleep(2)
        damage = (enemyAttack - self.defense) - mitigationRoll
        if damage >= 0:
            log("{} takes {} damage".format(self.name, damage), "fight")
            self.health = self.health - damage
        else:
            log("{} takes no damage!".format(self.name), "fight")
        if self.health <= 0:
            self.alive = False
            self.health = 0


class Ranger(Entity):
    """
    Ranger

    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Ranger")
        self.initMod += 3


class Scribe(Entity):
    """
    Scribe

    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Scribe")
        self.elementalSides = 2

    def attackTurn(self, enemy):
        elementalDamage = self.roll(self.elementalSides)
        enemy.takeDamage(self.attackRoll() + elementalDamage)


class Sorcerer(Entity):
    """
    Sorcerer

    """
    def __init__(self, name, hp, atk, d, im):
        Entity.__init__(self, name, hp, atk, d, im, "Sorcerer")
        self.spell_casts = 0
        self.spell_sides = 6

    def castSpell(self, enemy):
        self.spell_casts += 1
        spell = self.roll(self.spell_sides)
        if spell > 3:
            self.attackTurn(enemy, spell)
        else:
            self.attackTurn(enemy)

    def attackTurn(self, enemy, spellDamage=0):
        enemy.takeDamage(self.attackRoll() + spellDamage)


def log(message, m_type=None):
    if (m_type == "fight"):
        print(message)
        time.sleep(2)
        return
    if (m_type == "title"):
        message = "\n" + message + "\n"
        print("-"*25)
        print(message)
        print("-"*25)
        return
    print(message)


def user_continue(message="Press enter to continue"):
    message = "\n" + message + "\n"
    input(message)


def initial_battle_roll(a, b):
    a.initRoll()
    b.initRoll()
    log("{}'s initiative roll is {}".format(a.name, a.initiative), "fight")
    log("{}'s initiative roll is {}".format(b.name, b.initiative), "fight")


def fight(a, b):
    log("{} attacks!".format(a.name), "fight")
    a.attackTurn(b)

    if b.alive:
        log("{} attacks!".format(b.name), "fight")
        b.attackTurn(a)

        if not a.alive:
            log("{} has been defeated!".format(a.name), "fight")
            b.victories += 1
    else:
        log("{} has been defeated!".format(b.name), "fight")
        a.victories += 1


def fighter_health_info(a, b):
    log("{}'s Health: {}".format(a.name, a.health))
    log("{}'s Health: {}".format(b.name, b.health))


def battle(a, b):
    log("A Fight between {} a {} and {} a {}".format(a.name,
                                                     a.type,
                                                     b.name,
                                                     b.type),
                                                     "fight")
    initial_battle_roll(a, b)
    rounds = 1
    while a.alive and b.alive:
        log("-"*25)
        log("Round: {}".format(rounds))
        fighter_health_info(a, b)
        user_continue()
        if a.initiative >= b.initiative:
            fight(a, b)
        else:
            fight(b, a)
        rounds += 1
    log("The fight is finished", "fight")
    log("-"*25)
    return a, b


def determine_profession(choice, name):
    """
    Given a choice ('string')
    and a name ('string')

    return a profession of the players choice
    """
    if choice == "barbarian":
        return Barbarian(name, 20, 0, 0, 0)
    elif choice == "drunkard":
        return Drunkard(name, 14, 1, 1, -2)
    elif choice == "knight":
        return Knight(name, 12, 1, 1, -1)
    elif choice == "priest":
        return Priest(name, 10, 0, 0, 0)
    elif choice == "ranger":
        return Ranger(name, 10, 0, 0, 3)
    elif choice == "rogue":
        return Rogue(name, 8, 0, 0, 1)
    elif choice == "scribe":
        return Scribe(name, 10, 0, 0, 0)
    elif choice == "sorcerer":
        return Sorcerer(name, 10, 0, 0, 0)


def create_character():
    """
    Get class and name from user via terminal input

    create an object based on class chosen.

    return: player
    """
    log("Available Classes:\n[barbarian, drunkard, knight,"
        "priest, rogue, ranger, scribe, sorcerer]\n")
    choices = ["barbarian", "drunkard", "knight", "priest",
               "rogue", "ranger", "scribe", "sorcerer"]
    chosen = False

    while not chosen:
        choice = input("Choice a class: ")
        choice = choice.lower()
        if choice in choices:
            chosen = True
        else:
            user_continue("Not available. Press enter to try again.")

    name = input("Enter a name: ")
    if name == "":
        name = "Frit"
    return determine_profession(choice, name)


def game_intro(intro):
    """
    Welcome screen
    """
    intro = "\n" + intro + "\n"
    log(intro)
    character = create_character()
    input("\nPress enter to begin campaign\n")
    return character


def start_story(title, story):
    """
    Assuming introductions are paragraphs long,
    this is a way to print sentence by sentence
    for the player to read
    """
    story = story.split('.')
    log(title, "title")
    for sentence in story:
        log(sentence, "fight")
        log("-"*25)
    user_continue()


def introduce_character(player):
    player_intro = "You are {}. Born into a small village," \
                   " you've worked to become a strong {}.\n\n" \
                   "You are about to face your toughest challenge yet.." \
                   .format(player.name, player.type)
    log(player_intro)
    user_continue()


def encounter(intro, outro, player, enemies):
    log(intro, "fight")
    log("There are {} enemies in this encounter!".format(len(enemies)))
    user_continue()
    for enemy in enemies:
        player, enemy = battle(player, enemy)
        player.initiative = 0
        if player.alive:
            user_continue("Continue...")
        else:
            save_player_to_eternal_glory(player)
            log("Gameover")
            exit(1)
    log(outro, "fight")
    user_continue()


def database_check():
    """
    Database stuff
    """
    players = "players_table"
    games = "games_table"
    name = "name"
    name_type = "TEXT"
    victories = "victories"
    victories_type = "INTEGER"

    connection = sqlite3.connect(sqlite_file)
    cursor = connection.cursor()

    # create new table
    cursor.execute('CREATE TABLE IF NOT EXISTS {}'
                    '(id INTEGER PRIMARY KEY, {} {}, class TEXT, {} {})'
        .format(players, name, name_type, victories, victories_type))

    connection.commit()
    connection.close()


def save_player_to_eternal_glory(player):
    connection = sqlite3.connect(sqlite_file)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO players_table VALUES (null, ?,?,?)",
        [player.name,
        player.type,
        player.victories]
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    database_check()

    player = game_intro("Welcome to Roust")

    start_story("Roust", "")

    introduce_character(player)

    rakka = Barbarian("Rakka", 5, 0, 0, 0)
    zakka = Barbarian("Zakka", 6, 0, 0, 0)
    grug = Barbarian("Grug", 4, 0, 0, 0)
    a = Barbarian("Shim", 11, 1, 0, 1)
    b = Drunkard("Flek", 10, 0, 0, 0)
    c = Rogue("Dram", 7, 1, 1, 1)
    e = Barbarian("Puum", 16, 2, 4, 1)
    f = Drunkard("Clak", 17, 4, 3, 0)
    g = Rogue("Adrata", 14, 3, 2, 1)
    h = Sorcerer("Wrikka", 9, 5, 3, 2)

    first_enemy_group = [rakka, zakka, grug]
    second_enemy_group = [a, b, c]
    third_enemy_group = [e, f, g, h]

    intro = "An enemy is approaching!\n"
    outro = "You have completed the mission!\nThe people thank you!"

    encounter(intro, outro, player, first_enemy_group)

    print("\nYou gain exp and regain full health!\n")
    player.max_health += 5
    player.attack += 2
    player.defense += 2
    player.initMod += 1
    player.initiative = 0
    player.health = player.max_health
    print(player)
    user_continue()


    intro = "\nThere are stories saying these attacks are happening all over...\n" \
    "\nYou make towards the nearest village and find it is true!\n" \
    "\nHurriedly you make for a group of attackers!\n"

    encounter(intro, outro, player, second_enemy_group)

    print("\nYou gain exp and regain full health!\n")
    player.max_health += 10
    player.attack += 3
    player.defense += 3
    player.initMod += 2
    player.initiative = 0
    player.health = player.max_health
    print(player)
    user_continue()


    intro = "\nIt is true these attacks are happening to all nearby villages!\n" \
    "\nYou travel your fastest to help the next village\n" \
    "\nAlso you make it a point this time to find the location of Roust!\n"


    encounter(intro, outro, player, third_enemy_group)

    print("\nYou gain exp and regain full health!\n")
    player.max_health += 10
    player.attack += 3
    player.defense += 3
    player.initMod += 2
    player.initiative = 0
    player.health = player.max_health
    print(player)
    user_continue()

    print("\nYou have found the location of Roust from a dying enemy's pleads for mercy.\n")
    input("\nPress enter to continue\n")
    roust = Rogue("Roust", 25, 10, 8, 10)
    player, roust = battle(player, roust)
    if player.alive:
        log("\nCongratulations on saving the world\n")
    else:
        log("Gameover")
    save_player_to_eternal_glory(player)
    exit(1)
