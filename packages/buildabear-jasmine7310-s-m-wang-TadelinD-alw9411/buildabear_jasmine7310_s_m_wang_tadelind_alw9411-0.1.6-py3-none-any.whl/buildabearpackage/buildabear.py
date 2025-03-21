import time
import random

data = open('Data.txt', 'r') 
happyLine = data.readline().split(":")
happiness = int(happyLine[1].strip())

hungerLine = data.readline().split(":")
hunger = int(hungerLine[1].strip())

cleanLine = data.readline().split(":")
cleanliness = int(cleanLine[1].strip())

foodLine = data.readline().split(":")
food = int(foodLine[1].strip())

budgetLine = data.readline().split(":")
budget = int(budgetLine[1].strip())

nameLine = data.readline().split(":")
name = nameLine[1].strip()

initializedLine = data.readline().split(":")
if initializedLine[1] == "False\n":
    initialized = False
else:
    initialized = True

lastCheckedLine = data.readline().split(":")
lastChecked = round(int(lastCheckedLine[1]))

data.close()

# need variables for timer/ clock


# - We might need to create a quit function
#   that saves the data to a local DB to save progress
# - Restart/ die funtion
# ^^^^ OPTIONAL IMPLEMENTATION

# ******** Alex
# This function sets up the inital pet
# and starts the clock/ timing for
# hunger, cleanliness, and happiness to go down
# Also show initial startup diaglogue & instructions
# Something like : Hi! I'm Bear! Nice to meet you!
# Feed me to keep me happy! Work a job to earn money!... etc
# MOST IMPORTANT DIRECTION:
# TELL USER TO USE check_status after using play to check on pet
# play is only the initializer!!!!
# !!!! SET INITIALIZED TO TRUE AFTER!!!
# !!!!! MIGHT NEED TO CHANGE THIS LATER IN MAIN WHEN RUN/ PACKAGE AND NOT AS A FUNCTION!!!!!
def play():
    global happiness, hunger, cleanliness, initialized, lastChecked
    if not initialized:
        print()
        initialized = True
        happiness = 100
        hunger = 100
        cleanliness = 100
        lastChecked = round(time.time())
        print("ʕっ•ᴥ•ʔっ")
        print("Hi! I'm Bear! Nice to meet you!")
        print("Feed me to keep me happy! Work a job to earn money!")
        print("Use check_status to check my current happiness, hunger, and cleanliness!")
        return
    else:
        print("Already playing!")
        return False




# ******** Jasmine
# This function prints out the current status of the pet
# along with the correct emoticons
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def check_status():
    if initialized:
        update_status()
        # Status with least amount of points is prioritized
        if (hunger < 20) or (happiness < 20) or (cleanliness < 20):
            print("ʕx . xʔ")
            print(name + " is not doing so well.....")
        elif (hunger < 40) or (happiness < 40) or (cleanliness < 40):
            print("ʕ ´•̥̥̥ ᴥ•̥̥̥`ʔ")
            print(name + " is super sad you aren't taking care of it!!")
        elif (hunger < 60) or (happiness < 60) or (cleanliness < 60):
            print("ʕ´• ᴥ•̥`ʔ")
            print(name + " feels a little unhappy")
        elif (hunger < 80) or (happiness < 80) or (cleanliness < 80):
            print("＼ʕ •ᴥ•ʔ／")
            print(name + " is doing good!")
        elif (hunger < 100) or (happiness < 100) or (cleanliness < 100):
            print("✿ ✿ ✿ ┏ʕ •ᴥ•ʔ┛ ✿ ✿ ✿")
            print(name + " feels great! Good job!")
        elif (hunger < 120) or (happiness < 120) or (cleanliness < 120):
            print("*:・ﾟʕ◉ᴥ◉ʔ*:・ﾟ")
            print(name + " feels estatic! Are you sure you aren't spoiling " + name + "too much?")
        elif (hunger < 140) or (happiness < 140) or (cleanliness < 140):
            print("ʕʘ̅͜ʘ̅ʔ 🌎")
            print(name + " feels like it could take over the world! Hahaha!!! Should we be worried..?")
        elif (hunger < 160) or (happiness < 160) or (cleanliness < 160):
            print("ʕ•̫͡•ʕ*̫͡*ʕ•͓͡•ʔ-̫͡-ʕ•̫͡•ʔ*̫͡*ʔ-̫͡-ʔฅʕ •ع• ʔฅʕ•̫͡•ʕ*̫͡*ʕ•͓͡•ʔ-̫͡-ʕ•̫͡•ʔ*̫͡*ʔ-̫͡-ʔ")
            print("You're spoiling " + name + " too much. Look at what you've done. ")
            print(name +" can now use shadow clone jitsu and its your fault.")
        elif (hunger < 200) or (happiness < 200) or (cleanliness < 200):
            print(" __         __ ")
            print("/  \\.-----./  \\")
            print("\\    -   -    /")
            print(" |   o   o   | ")
            print(" \\  .-...-.  / ")
            print("   -\\__Y__/-   ")
            print("      ---      ")
            print("You've created the ultimate lifeform. Congratulations 🎉🎉🎉")

        print("-----------------------------------------------")
        print("")

        print("🍉 Hunger: " + str(hunger) + "%")
        print("🥹  Happiness: " + str(happiness) + "%")
        print("🚿 Cleanliness: " + str(cleanliness) + "%")
        print("💵 Balance: $" + str(budget))  
        return
    else:
        print("Make sure to use play() to set up the bear!")
        return

# ******** Jasmine
# This function uses the clock/ timer to update the
# hunger, happiness, and cleanliness over time
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def update_status():
    global happiness, hunger, cleanliness, initialized, lastChecked

    if initialized:
        update_cleanliness()
        update_happiness()
        update_hunger()
        lastChecked = round(time.time())
        return
    else:
        print("Make sure to use play() to set up the bear!")
        return


# ******** Sophia
# This function allows the user to change the name of the pet
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def change_name(temp):
    global name, initialized
    if initialized:
        if temp == "":
            print("You must enter a name.")
        else:
            name = temp

        return
    else:
        print("Make sure to use play() to set up the bear!")
        return

# ******** Alex
# This function uses the timer/ clock to periodically update the happiness
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def update_happiness():
    global initialized, happiness, lastChecked
    if not initialized:
        print("Make sure to use play() to set up the bear!")
        return
    if initialized:
        time_elapsed = round(int(time.time() - lastChecked))
        happiness -= time_elapsed
        happiness = max(happiness, 0)
        return

# ******** Tadelin
# This function uses the timer/ clock to periodically update the cleanliness
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def update_cleanliness():
    global initialized, cleanliness, lastChecked
    if not initialized:
        print("Make sure to use play() to set up the bear!")
        return
    if initialized:
        time_elapsed = round(int(time.time() - lastChecked))
        cleanliness -= time_elapsed
        cleanliness = max(cleanliness, 0)
        return

# ******** Tadelin
# This function uses the timer/ clock to periodically update the hunger
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def update_hunger():

    global initialized, hunger, lastChecked
    if not initialized:
        print("Make sure to use play() to set up the bear!")
        return
    if initialized:
        time_elapsed = round(int(time.time() - lastChecked))
        hunger -= time_elapsed
        hunger = max(hunger, 0)
        return


# ******** Sophia
# This function takes a certain int of hours to work
# $16/ hour (or how many you want)
# Updates budget!!
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def work(hours: int):
    global budget, initialized, name
    if initialized:
        budget = budget + (int(hours)*16)
        print(name+" worked for "+str(hours)+" hours. You earned "+str(int(hours)*16)+" coin.")
        return
    else:
        print("Make sure to use play() to set up the bear!")
        return

# ******** Sophia
# This function allows the user to buy food for a set int amount
# THIS FUNCTION CAN ONLY RUN IF PLAY() IS CALLED
# (INITIALIZED == TRUE)
# IF NOT INIT, PRINT DIRECTION TO CALL PLAY()
def buy_food(amount: int):
    global food, budget, initialized
    if initialized:
        #for now, food costs $1
        cost = 1
        if (int(amount)*cost > budget):
            print("You don't have enough money!")
        else:
            food = food+int(amount)
            budget = int(budget) - int(amount)*cost
            print("You bought "+str(amount)+" for "+str(int(amount)*cost)+" coin")
            
        return
    else:
        print("Make sure to use play() to set up the bear!")
        return


def feed_bear(amount : int):
    global name, hunger, food, happiness
    if not initialized:
        print("Make sure to use play() to set up the bear!")
        return
    update_status()
    if initialized:
        if amount == 0:
            print("Please enter an amount more than 0.")
        elif food >= amount:
            print("You gave " + name + " " + str(amount) +" jar(s) of honey!")
            print()
            print("ʕっ•ᴥ•ʔっ🍯")
            print("Their hunger has gone up by "+ str(10 * amount)+" points!")
            food -= amount
            hunger += (10 * amount)
        elif food < amount:
            print("You don't have enough food!")
            print("This makes " + name + "sad")
            print()
            print("ʕ ´•̥̥̥ ᴥ•̥̥̥`ʔ")
            print("Their happiness has decreased by 10.")
            print("Use the buy food command to get more food!")
            happiness -= 10
        
        return


def clean_bear():
    global name, cleanliness
    if not initialized:
        print("Make sure to use play() to set up the bear!")
        return
    update_status()
    if initialized:
        print("You gave " + name + " a bath!")
        print()
        print("🧼💦🫧 ₍ᐢ•ﻌ•ᐢ₎*:・ﾟ🧼💦🫧")
        print("They are feeling so clean!")
        print("Their cleanliness has gone up by 30 points!")
        cleanliness += 30
        return

def play_with_bear():
    global name, happiness
    if not initialized:
        print("Make sure to use play() to set up the bear!")
        return
    update_status()
    if initialized:
        event = random.randint(0,3)
        if event == 0:
            print("You watched a movie with " + name + "!")
            print()
            print("ʕ •ᴥ•ʔ🍿     ˙✧˖°📺 ⋆｡˚")
            print("They loved the movie!")
            print("Their happiness has gone up by 20 points!")
            happiness += 20
        elif event == 1:
            print("You had a dance party with " + name + "!")
            print()
            print("ヾʕ ˃ᴥ˂ ʔ◞ • *✰")
            print("They had a groovy time with you!")
            print("Their happiness has gone up by 20 points!")
            happiness += 20
        elif event == 2:
            print("You played fetch with " + name + "!")
            print()
            print("                          ᳂          ")
            print("       ┏ʕ •ᴥ•ʔ┛                      ")
            print("They had such a fun time!")
            print("Their happiness has gone up by 20 points!")
            happiness += 20
        elif event == 3:
            print("You picked flowers with " + name + "!")
            print()
            print("🌼  💐ʕ•ᴥ• ʔ  🌼")
            print("They made you a bouquet!")
            print("Their happiness has gone up by 20 points!")
            happiness += 20
        
        return



