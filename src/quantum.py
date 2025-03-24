import fpp
import os

aaaaan = 0
while True:
    while aaaaan < 1:
        print("Welcome to Quantum. Its ide for F++. Current version is 0.2.1")
        print("Type 'exit' to exit and 'help' to see commands")
        aaaaan += 1
    text = input("Quantum > ")
    if text == "exit":
        confirm = input("Are you sure you want to exit? (yes/no): ")
        if confirm.lower() == "yes" or confirm.lower() == "y" or confirm.lower() == "yeah":
            break
        else:
            continue
    elif text == "release notes":
        print("Current version is 0.2.1 (Release-24032025)")
        print("- Some small changes")
        continue
    elif text == "help":
        print("Type 'exit' to exit")
        print("Type 'release notes' to see release notes")
        print("Type 'help' to see help")
        continue

    result, error = fpp.run('<stdin>' ,text)

    if error: print(error.as_string())
    elif result: print(result)
