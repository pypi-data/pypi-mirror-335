import random
import math
import hashlib

def generate(length):
    '''
    This function generates a password of a given length
    '''
    if type(length) != int:
        raise ValueError("Length Must be an integer!!")
    list_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    all_chars = list_lowercase
    password = [random.choice(list_lowercase)]
    while len(password) < length:
        password.append(random.choice(all_chars))
    return ''.join(password)


#does a cesar cipher on a string
def caesar_cipher(word, shift):
    '''
    This functions implements a caesar cipher on an inputted password, 
    where a shift is inputted to shift the letters by a certain amount.
    '''
    if type(word) != str:
        raise ValueError("Input must be a string!")
    if type(shift) != int:
        raise ValueError("Shift must be an int")
    try:
        tempShift = int(shift)
    except ValueError:
        raise ValueError("Shift must be an int")
    if float(shift) % 1 != 0.0:
        raise ValueError("Shift must be an int")
    if not (1 <= tempShift <= 25):
        raise ValueError("Shift value must be between 1 and 25.")
    def shift_letter(char, shift):
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            return chr((ord(char) - base + shift) % 26 + base)
        return char

    return ''.join(shift_letter(char, tempShift) for char in word)


def scramble(string):
    '''
    This function scrambles an inputted password and returns the scrambled version.
    '''
    if type(string) != str:
        raise ValueError("Input must be a string!")
    toList = [chr for chr in string]
    retString = ''
    while len(toList) > 0:
        rand = math.floor(random.random() * len(toList))
        letter = toList.pop(rand)
        retString = retString + letter
    return retString

def binary_password(l):
    '''
    This function generates a binary password of a given length.
    '''
    if type(l) != int:
        raise ValueError("Length input must be an integer!")
    retString = ''
    for _ in range(l):
        retString+= str(random.randint(0,1))
    return retString

def generateHash(password):
    '''
    This function generates a hash of an inputted password.
    '''
    if type(password) != str:
        raise ValueError("Password must be a string")
    return hashlib.sha256(password.encode()).hexdigest()

def getFunnyPassword():
    '''
    This function generates a funny password. 
    '''
    funny_list_1 = list('123456789')
    funny_list_2= ["sleepy", "hungry", "tired", "angry", "happy", "sad", "excited", "confused", "bored", "nervous", "excited", "happy", "sad", "angry", "tired", "sleepy", "hungry", "bored", "confused", "nervous"]
    funny_list_3= ["cats", "dogs", "birds", "fish", "snakes", "cows", "horses", "sheep", "goats", "pigs", "chickens", "ducks", "turkeys", "geese", "peacocks", "parrots", "penguins", "ostriches", "eagles", "owls", "sparrows", "roosters", "hens", "peahens", "roosters"]
    funny_list_4= ["orange", "red", "blue", "green", "yellow", "purple", "pink", "brown", "black", "white", "gray", "gold", "silver", "bronze", "copper", "iron", "steel", "gold", "silver", "bronze", "copper", "iron", "steel"]
    return random.choice(funny_list_1) + random.choice(funny_list_2) + random.choice(funny_list_4) + random.choice(funny_list_3)


