![Python build & test](https://github.com/software-students-spring2025/3-python-package-package-bear/actions/workflows/build.yaml/badge.svg)

# Python Package Exercise: Package Bear 🐻🐻‍❄️🐼

## Package Description
Your own command line bear!

## Team Members
Jasmine Fan https://github.com/jasmine7310

Sophia Wang https://github.com/s-m-wang

Tadelin De Leon https://github.com/TadelinD

Alex Wang https://github.com/alw9411

## Contents
### buildabear.py
Contains all functions used to initialize, interact, and play with bear.

**change_name(temp)**

> change the name of the bear

- *Parameters*:
`temp`- the name to change the name of the bear into

- *Return*: nothing

**work(hours)**

> work a number of int hours to earn coins

- *Parameters*:
`hours`- int number of hours worked

- *Return*: nothing

**buy_food(amount)**

> buy a set amount of food

- *Parameters*:
`amount`- the int amount of food to buy

- *Return*: nothing

**feed_bear(amount)**

> feed an amount of food to the bear

- *Parameters*:
`amount`- the int amount of food to feed the bear

- *Return*: nothing

## Configuration
Before installing if you don't have pipenv:

```
pip install pipenv
```

Then activate pipenv:
```
pipenv shell
```

On a new python project run:
```
pip install buildabear-jasmine7310-s-m-wang-TadelinD-alw9411
```
*PLEASE CREATE A DATA.TXT FILE AS SPECIFIED [HERE](#set-up-environment-variables-and-starter-data) BEFORE PROCEEDING!!!*

First use the command below for the welcome message
```
python -m buildabearpackage
```

Then use the command below to initialize the package
```
python -m buildabearpackage start
```
## Set Up Environment Variables and Starter Data
To use the package you are going to need to create a file called Data.txt in the same directory in which you will use the package. 

In this txt file you will need to copy and paste the following:
```
happiness:100
hunger:100
cleanliness:100
food:10
budget:1000
name:Bear
initialized:False
lastChecked:0
```
Make sure that there is no new line after inputting this information.

## Interacting with Pet
Once the Data.txt file is set up, you are ready to interact with your pet.
```
python -m buildabearpackage status
python -m buildabearpackage "change name"
python -m buildabearpackage work X  # X being an integer number!!
python -m buildabearpackage feed X # X being an interger number!!
python -m buildabearpackage clean
python -m buildabearpackage play
python -m buildabearpackage "buy food" X  # X being an integer number!!
```

## Link to Our Package Page
[Package Bear: buildabear](https://pypi.org/project/buildabear-jasmine7310-s-m-wang-TadelinD-alw9411/)

## Project Contribution

### Virtual Environment Setup
```
pip install pipenv
pipenv install pytest
pytest
pipenv shell
```
### Uploading to Pypi using Twine
If there are *.egg-info and dist directories delete them before proceeding. Be sure to update version number.

```
pip install build twine
python -m build
twine upload dist/*
```

## Example Usage
[Link to Example Usage Markdown](https://github.com/software-students-spring2025/3-python-package-package-bear/blob/main/example.md)