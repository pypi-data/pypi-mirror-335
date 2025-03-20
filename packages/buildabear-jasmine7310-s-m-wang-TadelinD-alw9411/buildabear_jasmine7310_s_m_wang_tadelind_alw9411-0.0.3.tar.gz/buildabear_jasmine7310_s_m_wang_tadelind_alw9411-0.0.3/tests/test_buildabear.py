import pytest
from src.buildabearpackage import buildabear
import unittest
from unittest.mock import patch
import time

class Test(unittest.TestCase):


    #test initialization
    def test_initialization(self):
        buildabear.play()
        assert buildabear.initialized == True, f"Expected buildabear to be initialized"
    
    def test_initial_stats(self):
        buildabear.initialized = False
        buildabear.play()
        assert buildabear.happiness == 100, f"Expected happiness to be 100, was {buildabear.happiness}"
        assert buildabear.cleanliness == 100, f"Expected cleanliness to be 100, was {buildabear.cleanliness}"
        assert buildabear.hunger == 100, f"Expected hunger to be 100, was {buildabear.hunger}"
        
    def test_double_initialization(self):
        buildabear.initialized = False
        buildabear.play()
        assert not buildabear.play(), f"Expected initialization after already initialized to return False"
        
    #test update happiness
    def check_time_updated_happiness(self):
        curr_time = buildabear.lastChecked
        time.sleep(1)
        buildabear.update_happiness()
        assert curr_time != buildabear.lastChecked, f"Update happiness function not updating time"
    
    def check_happiness_updated(self):
        buildabear.happiness = 100
        buildabear.lastChecked = time.time()
        time.sleep(1)
        buildabear.update_happiness()
        assert buildabear.happiness == 99, f"Expected buildabear happiness to be 99. It was {buildabear.happiness}"
        
    def check_happiness_nonnegative(self):
        buildabear.happiness = 0
        buildabear.lastChecked = time.time()
        time.sleep(1)
        buildabear.update_happiness()
        assert buildabear.happiness == 0, f"Expected buildabear happiness to be 0. It was {buildabear.happiness}"

        # test update cleanliness

    def check_time_updated_cleanliness(self):
        curr_time = buildabear.lastChecked
        time.sleep(1)
        buildabear.update_cleanliness()
        assert curr_time != buildabear.lastChecked, f"Update cleanliness function not updating time"

    def check_cleanliness_updated(self):
        buildabear.cleanliness = 100
        buildabear.lastChecked = time.time()
        time.sleep(1)
        buildabear.update_cleanliness()
        assert buildabear.cleanliness == 99, f"Expected buildabear cleanliness to be 99. It was {buildabear.cleanliness}"

    def check_cleanliness_nonnegative(self):
        buildabear.cleanliness = 0
        buildabear.lastChecked = time.time()
        time.sleep(1)
        buildabear.update_cleanliness()
        assert buildabear.cleanliness == 0, f"Expected buildabear cleanliness to be 0. It was {buildabear.cleanliness}"

        # test update hunger

    def check_time_updated_hunger(self):
        curr_time = buildabear.lastChecked
        time.sleep(1)
        buildabear.update_hunger()
        assert curr_time != buildabear.lastChecked, f"Update hunger function not updating time"

    def check_hunger_updated(self):
        buildabear.hunger = 100
        buildabear.lastChecked = time.time()
        time.sleep(1)
        buildabear.update_hunger()
        assert buildabear.hunger == 99, f"Expected buildabear hunger to be 99. It was {buildabear.hunger}"

    def check_hunger_nonnegative(self):
        buildabear.hunger = 0
        buildabear.lastChecked = time.time()
        time.sleep(1)
        buildabear.update_hunger()
        assert buildabear.hunger == 0, f"Expected buildabear hunger to be 0. It was {buildabear.hunger}"

    #buy food tests
    def test_buy_food(self):
            #test that it actually modifies the budget and food
            buildabear.initialized = True
            buildabear.budget = 100
            buildabear.buy_food(1)
            assert buildabear.budget == 99, f"Expected buy_food() to return 99. Instead it returned {buildabear.budget}."
        
    
    def test_buy_food_negative(self):
        #test that food does not go into the negatives/not enough money
        buildabear.initialized = True
        buildabear.budget = 0
        for i in range(10):
            buildabear.buy_food(1)
            assert buildabear.budget == 0, f"Expected buy_food() to return 0. Instead it returned {buildabear.budget}."

    
    def test_buy_food_multiple(self):
        #test the scenario where you buy multiple amounts of food
        buildabear.initialized = True
        buildabear.budget = 100
        for i in range(10):
            buildabear.buy_food(2)
        assert buildabear.budget == 80, f"Expected buy_food() to return 80. Instead it returned {buildabear.budget}."

    #work tests
    #check work for 1 hour multiple times
    def test_work_once(self):
        buildabear.initialized = True
        buildabear.budget = 0
        buildabear.work(100)
        assert buildabear.budget == 1600, f"Expected work() to return 1600. Instead it returned {buildabear.budget}."

    #check work for 0
    def test_work_none(self):
        buildabear.initialized = True
        buildabear.budget = 0
        buildabear.work(0)
        assert buildabear.budget == 0, f"Expected work() to return 0. Instead it returned {buildabear.budget}."
            
    #check work for multiple hours multiple times
    def test_work_none(self):
        buildabear.initialized = True
        buildabear.budget = 0
        buildabear.work(200)
        assert buildabear.budget == 3200, f"Expected work() to return 3200. Instead it returned {buildabear.budget}."
        
    
    #change name tests
    #check change name normally once
    def test_change_name_once(self):
        buildabear.initialized = True
        buildabear.name = "Bear"
        buildabear.change_name("Bear Test")
        assert buildabear.name != "Bear", f"Expected change_name() to return Bear Test. Instead it returned {buildabear.name}."
        
    #check change name with multiple names
    def test_change_name_multiple(self):
        buildabear.initialized = True
        buildabear.name = "Bear"
        names = ["bear1","bear2","bear3"]
        for i in range (3):
            buildabear.change_name(names[i])
            assert buildabear.name == names[i], f"Expected change_name() to return {names[i]}. Instead it returned {buildabear.name}."
        
    #check change name for empty string
    def test_change_name_empty(self):
        buildabear.initialized = True
        buildabear.name = "Bear"
        buildabear.change_name("")
        assert buildabear.name == "Bear", f"Expected change_name() to return Bear. Instead it returned an empty string."
       

    #feed bear tests
    def test_feed_bear_increase(self):
        buildabear.food = 2
        buildabear.hunger = 20
        buildabear.lastChecked = time.time()
        buildabear.feed_bear()
        assert buildabear.hunger == 30, f"Expected hunger variable to be 30. Instead it returned {buildabear.hunger}."
    
    def test_feed_bear_food_count(self):
        buildabear.food = 2
        buildabear.lastChecked = time.time()
        buildabear.feed_bear()
        assert buildabear.food == 1, f"Expected food variable to be 1. Instead it returned {buildabear.food}."

    def test_feed_bear_no_food(self):
        buildabear.food = 0
        buildabear.hunger = 20
        buildabear.happiness = 30
        buildabear.lastChecked = time.time()
        buildabear.feed_bear()
        assert buildabear.food == 0, f"Expected food variable to be 0. Instead it returned {buildabear.food}."
        assert buildabear.hunger == 20, f"Expected hunger variable to be 20. Instead it returned {buildabear.hunger}."
        assert buildabear.happiness == 20, f"Expected happiness variable to be 20. Instead it returned {buildabear.happiness}."
    
    #clean bear tests
    def test_clean_bear_increase(self):
        buildabear.cleanliness = 20
        buildabear.lastChecked = time.time()
        buildabear.clean_bear()
        assert buildabear.cleanliness == 50, f"Expected cleanliness variable to be 50. Instead it returned {buildabear.cleanliness}."

    def test_clean_bear_multiple(self):
        buildabear.cleanliness = 0
        buildabear.lastChecked = time.time()
        for i in range(3):
            buildabear.clean_bear()
        assert buildabear.cleanliness == 90, f"Expected cleanliness variable to be 90. Instead it returned {buildabear.cleanliness}."
    
    def test_clean_bear_time_passed(self):
        buildabear.cleanliness = 20
        buildabear.lastChecked = time.time()
        time.sleep(3)
        buildabear.clean_bear()
        assert buildabear.cleanliness == 47, f"Expected cleanliness variable to be 47. Instead it returned {buildabear.cleanliness}."

    #play with bear tests
    def test_play_bear_increase(self):
        buildabear.happiness = 20
        buildabear.lastChecked = time.time()
        buildabear.play_with_bear()
        assert buildabear.happiness == 40, f"Expected happiness variable to be 40. Instead it returned {buildabear.happiness}."
    
    def test_play_bear_multiple(self):
        buildabear.happiness = 0
        buildabear.lastChecked = time.time()
        for i in range(3):
            buildabear.play_with_bear()
        assert buildabear.happiness == 60, f"Expected happiness variable to be 60. Instead it returned {buildabear.happiness}."

    def test_play_bear_time_passed(self):
        buildabear.happiness = 20
        buildabear.lastChecked = time.time()
        time.sleep(3)
        buildabear.play_with_bear()
        assert buildabear.happiness == 37, f"Expected happiness variable to be 37. Instead it returned {buildabear.happiness}."
    
    # Test check_status()
    @patch('builtins.print')
    def test_check_status_happiness(self, mock_print):
        # test the scenario where the happiness is the lowest 
        buildabear.initialized = True
        buildabear.happiness = 19
        buildabear.hunger = 100
        buildabear.cleanliness = 100
        buildabear.check_status()
        mock_print.assert_any_call("ʕx . xʔ")
        mock_print.assert_any_call(buildabear.name + " is not doing so well.....")
    
    @patch('builtins.print')
    def test_check_status_hunger(self, mock_print):
        # test the scenario where the hunger is the lowest 
        buildabear.initialized = True
        buildabear.happiness = 100
        buildabear.hunger = 39
        buildabear.cleanliness = 100
        buildabear.check_status()
        mock_print.assert_any_call("ʕ ´•̥̥̥ ᴥ•̥̥̥`ʔ")
        mock_print.assert_any_call(buildabear.name + " is super sad you aren't taking care of it!!")
    
    @patch('builtins.print')
    def test_check_status_cleanliness(self, mock_print):
        # test the scenario where the cleanliness is the lowest 
        buildabear.initialized = True
        buildabear.happiness = 100
        buildabear.hunger = 100
        buildabear.cleanliness = 79
        buildabear.lastChecked = time.time()
        buildabear.check_status()
        mock_print.assert_any_call("＼ʕ •ᴥ•ʔ／")
        mock_print.assert_any_call(buildabear.name + " is doing good!")

    # Test update_status()
    @patch('builtins.print')
    def test_update_status_happiness(self, mock_print):
        # test if update happiness correctly
        buildabear.initialized = False
        buildabear.happiness = 72
        buildabear.update_status()
        mock_print.assert_any_call("Make sure to use play() to set up the bear!")
    
    @patch('builtins.print')
    def test_update_status_hunger(self, mock_print):
        buildabear.initialized = False
        buildabear.hunger = 72
        buildabear.update_status()
        mock_print.assert_any_call("Make sure to use play() to set up the bear!")

    @patch('builtins.print')
    def test_update_status_cleanliness(self, mock_print):
        buildabear.initialized = False
        buildabear.happiness = 72
        buildabear.update_status()
        mock_print.assert_any_call("Make sure to use play() to set up the bear!")
