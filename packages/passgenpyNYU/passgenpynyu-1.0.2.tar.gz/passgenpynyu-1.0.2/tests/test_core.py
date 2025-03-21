import pytest
import hashlib
import string
import passgenpyNYU.core as core

def test_generate():
    password = core.generate(10)
    assert isinstance(password, str)
    assert len(password) == 10
    assert any(char.isalpha() for char in password)

def test_generate_upper():
    password = core.generate(10, capitalize = True)
    assert isinstance(password, str)
    assert any(char.isupper() for char in password)

def test_generate_number():
    password = core.generate(10, numbers = True)
    assert isinstance(password, str)
    assert any(char.isdigit() for char in password)

def test_generate_symbol():
    password = core.generate(10, symbols = True)
    assert isinstance(password, str)
    assert any(char in string.punctuation for char in password)

def test_generate_number_cap():
    password = core.generate(10, numbers = True, capitalize = True)
    assert isinstance(password, str)
    assert any(char.isdigit() for char in password)
    assert any(char.isupper() for char in password)

def test_generate_number_symbol():
    password = core.generate(10, numbers = True, symbols = True)
    assert isinstance(password, str)
    assert any(char.isdigit() for char in password)
    assert any(char in string.punctuation for char in password)

def test_generate_cap_symbol():
    password = core.generate(10, capitalize = True, symbols = True)
    assert isinstance(password, str)
    assert any(char.isupper() for char in password)
    assert any(char in string.punctuation for char in password)

def test_generate_number_cap_symbol():
    password = core.generate(10, numbers = True, capitalize = True, symbols = True)
    assert isinstance(password, str)
    assert any(char.isdigit() for char in password)
    assert any(char.isupper() for char in password)
    assert any(char in string.punctuation for char in password)

def test_basic_shift_cipher():
    assert core.caesar_cipher("hello", 3) == "khoor"
    assert core.caesar_cipher("abc", 2) == "cde"

def test_case_preservation_cipher():
    assert core.caesar_cipher("HeLLo", 3) == "KhOOr"

def test_non_alpha_chars_cipher():
    assert core.caesar_cipher("hello, world!", 5) == "mjqqt, btwqi!"
    assert core.caesar_cipher("1234", 4) == "1234"

def test_shift_boundaries_cipher():
    assert core.caesar_cipher("z", 1) == "a"
    assert core.caesar_cipher("a", 25) == "z"

def test_invalid_shifts_cipher():
    with pytest.raises(ValueError, match="Shift value must be between 1 and 25."):
        core.caesar_cipher("hello", 0)
    with pytest.raises(ValueError, match="Shift value must be between 1 and 25."):
        core.caesar_cipher("hello", 26)

def test_non_integer_shift_cipher():
    with pytest.raises(ValueError, match="Shift must be an int"):
        core.caesar_cipher("hello", "three")
    with pytest.raises(ValueError, match="Shift must be an int"):
        core.caesar_cipher("hello", 3.5)

def test_empty_string_cipher():
    assert core.caesar_cipher("", 5) == ""

def test_scramble():
    test_cases = ["hello", "shaurya", "asjdkd7832", "nsdkajkkadj!askd&", "kjaibbd88*jsd8"]
    for test in test_cases:
        scrambled_string = core.scramble(test)
        assert len(test) == len(scrambled_string)
        char_list_test = [char for char in test]
        char_list_scrambled = [char for char in scrambled_string]
        for char in char_list_test:
            assert char in char_list_scrambled

def test_empty_string_scramble():
    assert core.scramble("") == ""

def test_single_character_scramble():
    assert core.scramble("a") == "a"

def test_spaces_scramble():
    test_str = "hello world"
    scrambled = core.scramble(test_str)
    assert len(scrambled) == len(test_str)
    assert sorted(scrambled) == sorted(test_str)

def test_binary_password():
    bin_password = core.binary_password(10)
    assert isinstance(bin_password, str)
    assert len(bin_password) == 10
    bitlist = list('01')
    for char in bin_password:
        assert char in bitlist

def test_binary_password_randomness():
    bin_password = core.binary_password(10)
    bin_password2 = core.binary_password(10)
    assert bin_password != bin_password2

def test_binary_password_2():
    bin_password = core.binary_password(4)
    assert isinstance(bin_password, str)
    assert len(bin_password) == 4
    bitlist = list('01')
    for char in bin_password:
        assert char in bitlist

def test_generateHash():
    pass_hash = core.generateHash("password")
    assert isinstance(pass_hash, str)
    assert len(pass_hash) == 64

def test_generateHashRandomness():
    pass_hash = core.generateHash("asjdlasjdahhofhhwba7")
    pass_hash2 = core.generateHash("password")
    assert pass_hash != pass_hash2

def test_generate_hash_correctness():
    password = "NYC9sleepyorangecows"
    hash = core.generateHash(password)
    hash_t = core.generateHash(password)
    assert hash == hash_t

def test_generateHas_input():
    with pytest.raises(ValueError, match="Password must be a string"):
        core.generateHash(123)

def test_getFunnyPassword_type():
    funny_password = core.getFunnyPassword()
    assert isinstance(funny_password, str)
    assert len(funny_password) > 0

def test_getFunnyPassowrd_differences():
    results = [core.getFunnyPassword() for _ in range(5)]
    assert len(results) > 1

def test_getFunnycontents():
    funny_password = core.getFunnyPassword()
    funny_list_1 = list('123456789')
    funny_list_2= ["sleepy", "hungry", "tired", "angry", "happy", "sad", "excited", "confused", "bored", "nervous", "excited", "happy", "sad", "angry", "tired", "sleepy", "hungry", "bored", "confused", "nervous"]
    funny_list_3= ["cats", "dogs", "birds", "fish", "snakes", "cows", "horses", "sheep", "goats", "pigs", "chickens", "ducks", "turkeys", "geese", "peacocks", "parrots", "penguins", "ostriches", "eagles", "owls", "sparrows", "roosters", "hens", "peahens", "roosters"]
    funny_list_4= ["orange", "red", "blue", "green", "yellow", "purple", "pink", "brown", "black", "white", "gray", "gold", "silver", "bronze", "copper", "iron", "steel", "gold", "silver", "bronze", "copper", "iron", "steel"]
    assert any(item in funny_password for item in funny_list_1)
    assert any(item in funny_password for item in funny_list_2)
    assert any(item in funny_password for item in funny_list_3)
    assert any(item in funny_password for item in funny_list_4)

def test_invalid_length_generate():
    with pytest.raises(ValueError, match="Length Must be an integer!!"):
        core.generate("hello")

def test_invalid_capitalize_generate():
    with pytest.raises(ValueError, match="Capitalize Must be a boolean!!"):
        core.generate(10, capitalize=10)
    
def test_invalid_numbers_generate():
    with pytest.raises(ValueError, match="Numbers value must be a boolean!!"):
        core.generate(10, numbers=10)

def test_invalid_symbols_generate():
    with pytest.raises(ValueError, match="Symbols value must be a boolean!!"):
        core.generate(10, symbols=10)

def test_invalid_scramble():
    with pytest.raises(ValueError, match="Input must be a string!"):
        core.scramble(10)

def test_invalid_binary():
    with pytest.raises(ValueError, match= "Length input must be an integer!"):
        core.binary_password("test")