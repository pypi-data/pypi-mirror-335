import buildabearpackage.buildabear as buildabear
import sys

def main():
    # ^^ pass is to keep compiler happy 
    # (or else error saying expected indent)
    # DELETE PASS WHEN WORKING ON CODE!!!!
    if "start" in sys.argv[1:]:
        buildabear.play()
    elif "status" in sys.argv[1:]:
        buildabear.check_status()
    elif "change name" in sys.argv[1:]:
        temp = input("Enter a new name for your pet!")
        buildabear.change_name(temp)
    elif "work" in sys.argv[1:]:
        buildabear.work(sys.argv[2])
    elif "feed" in sys.argv[1:]:
        buildabear.feed_bear(int(sys.argv[2]))
    elif "clean" in sys.argv[1:]:
        buildabear.clean_bear()
    elif "play" in sys.argv[1:]:
        buildabear.play_with_bear()
    elif "buy food" in sys.argv[1:]:
        buildabear.buy_food(sys.argv[2])
    else:
        print("Welcome to Package Bear! Your very own command line pet!")
        print("Try using 'start' to create your bear!")
        print("Then use the commands below to interact with your pet:")
        print("\t status- check the status of your pet")
        print('\t "change name"- to change the name of your pet')
        print('\t work X- (X being an integer number) to work a number of X hours and earn money to buy food')
        print('\t feed- to feed your pet')
        print('\t clean- to clean your pet')
        print('\t play- to play with your pet')
        print('\t "buy food" X- (X being an integer number) to buy an X amount of food for your pet')

    data = open("Data.txt", "w")
    dataScript = "happiness:" + str(buildabear.happiness) + "\n"
    dataScript += "hunger:" + str(buildabear.hunger) + "\n"
    dataScript += "cleanliness:" + str(buildabear.cleanliness) + "\n"
    dataScript += "food:" + str(buildabear.food) + "\n"
    dataScript += "budget:" + str(buildabear.budget) + "\n"
    dataScript += "name:" + str(buildabear.name) + "\r"
    dataScript += "initialized:" + str(buildabear.initialized) + "\n"
    dataScript += "lastChecked:" + str(buildabear.lastChecked)
    data.write(dataScript)
    data.close()
    return
    


if __name__ == "__main__":
    main()