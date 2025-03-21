import sys
from passgenpyNYU import core
import argparse

def positive_int(val):
    try:
        value = int(val)
    except ValueError: 
        raise argparse.ArgumentTypeError("Invalid input. Must be a whole number greater than 0")
    
    if value <= 0: 
        raise argparse.ArgumentTypeError("Invalid Value. Must be greater than 0")
    
    return value

def parser():
    parser = argparse.ArgumentParser(
        description="Generate a funny or serious password"
    )

    parser.add_argument(
        "-g",
        "--generate",
        dest="generate",
        type= positive_int,
        help= "Generate a random password. Takes the following argument: length, capitalize= False, numbers= False, symbols= False",
    )

    parser.add_argument(
        "-c", 
        "--caesar_cipher",
        nargs=2,
        help= "Decode a string based on caesar cipher. Takes two arguments: string and int (between 1 and 25) for shift",
    )

    parser.add_argument(
        "-s", 
        "--scramble",
        dest= "scramble",
        help= "Scramble a string as a password. Takes one argument: string",
    )

    parser.add_argument(
        "-f",
        "--getFunnyPassword",
        dest= "funnyPassword",
        action= "store_true",
        help= "Get a funny password. No arguments"
    )

    parser.add_argument(
        "-b",
        "--binarypassword",
        dest= "binarypassword",
        type= positive_int,
        help= "Generate a binary password. Takes in length of string as argument."
    )

    parser.add_argument(
        "-gh",
        "--generatehash",
        dest= "generatehash",
        help= "Converts password into Hash. Takes in string as arugment"
    )

    return parser


def main(): 
    parse = parser()

    try:
        args = parse.parse_args()
    except argparse.ArgumentError as exc: 
        print("Error parsing arguments", str(exc))
        exit(-1)

    if args.generate is not None:
        print(core.generate(args.generate))

    if args.caesar_cipher:
        try:
            print(core.caesar_cipher(args.caesar_cipher[0], int(args.caesar_cipher[1])))
        except ValueError:
            print("Error Second Argument is not a valid integer between 1 and 25") 
    
    if args.generatehash:
        print(core.generateHash(args.generatehash))

    if args.binarypassword is not None:
        print(core.binary_password(int(args.binarypassword)))

    if args.scramble:
        print(core.scramble(args.scramble))

    if args.funnyPassword:
        print(core.getFunnyPassword())


if __name__ == "__main__":
    main()