import fpp
import os
import sys
from run import run_file



def run_prompt():
    aaaaan = 0
    lang = "eng"
    while True:
        while aaaaan < 1:
            if lang == "ukr":
                print("Вітаю в Quantum. Це IDE для мови програмування F++. Поточна версія - 2.0.0")
                print("Type 'exit' to exit and 'help' to see commands")
                aaaaan += 1
            else:
                print("Welcome to Quantum. Its ide for F++. Current version is 2.0.0")
                print("Type 'exit' to exit and 'help' to see commands")
                aaaaan += 1
                
        text = input("Quantum > ")
        if text.strip() == "": continue
        if lang == "ukr":
            if text == "exit":
                confirm = input("Ви впевнені, що хочете вийти? (yes/no): ")
                if confirm.lower() == "yes" or confirm.lower() == "y" or confirm.lower() == "так":
                    break
                else:
                    continue
        else:
            if text == "exit":
                confirm = input("Are you sure you want to exit? (yes/no): ")
                if confirm.lower() == "yes" or confirm.lower() == "y" or confirm.lower() == "yeah":
                    break
                else:
                    continue
        if lang == "ukr":
            if text == "release notes":
                print("Поточна версія - 2.0.0 (Release-31032025)")
                print("- підтримка компіляції інших файлів(альфа)")
                continue
        else:
            if text == "release notes":
                print("Current version is 2.0.0 (Release-31032025)")
                print("- Added support compiling other files(Alpha)")
           
                continue
        if lang == "ukr":
            if text == "help":
                print("Напишіть 'exit' щоб вийти")
                print("Напишіть 'release notes' щоб побачити релізні нотатки")
                print("Напишіть 'help' щоб отримати список команд")
                print("Напишіть 'clear' щоб очистити консоль")
                continue
        else:
            if text == "help":
                print("Type 'exit' to exit")
                print("Type 'release notes' to see release notes")
                print("Type 'help' to see help")
                print("Type 'clear' to clear console")
                continue
        if lang == "eng":
            if text.startswith("lang"):
                args = text.split()
                if len(args) == 1:
                    print("You not set language. Available languages: \n - English(100%) \n - Ukrainian(only terminal)")
                    continue
                elif args[1].lower() in ("eng", "english"):
                    if lang != "eng":
                        lang = "eng"
                        print("Language changed to 'English'")
                    else:
                        print("Language already set to 'English'")
                    continue
                elif args[1].lower() in ("ukr", "ua", "ukrainian"):
                    if lang != "ukr":
                        lang = "ukr"
                        print("Мову змінено на 'Українську'")
                    else:
                        print("Мова вже встановлена на 'Українську'")
                    continue
                else:
                    print("This language is not supported")
                    continue
        else:
            if text.startswith("lang"):
                args = text.split()
                if len(args) == 1:
                    print("Ви не вказали мову. Доступні мови: \n - Англійська(100%) \n - Українська(тільки термінал)")
                    continue
                elif args[1].lower() in ("eng", "english", "англ", "англійська"):
                    if lang != "eng":
                        lang = "eng"
                        print("Language changed to 'English'")
                    else:
                        print("Language already set to 'English'")
                    continue
                elif args[1].lower() in ("ukr", "ua", "ukrainian", "укр", "українська"):
                    if lang != "ukr":
                        lang = "ukr"
                        print("Мову змінено на 'Українську'")
                    else:
                        print("Мова вже встановлена на 'Українську'")
                    continue
                else:
                    print("Вказана непідтримна мова!")
                    continue
        if lang == "ukr":
            if text == "clear":
                confirm = input("Ви впевненіб що хочете очистити термінал? (yes/no): ")
                if confirm.lower() == "yes" or confirm.lower() == "y" or confirm.lower() == "так":
                    if os.name == 'nt':
                        os.system('cls')
                    else:
                        os.system('clear')
                else:
                    continue
            
                continue
        else:
            if text == "clear":
                confirm = input("Are you sure you want to clear terminal? (yes/no): ")
                if confirm.lower() == "yes" or confirm.lower() == "y" or confirm.lower() == "yeah":
                    if os.name == 'nt':
                        os.system('cls')
                    else:
                        os.system('clear')
                else:
                    continue
            
                continue
        context = fpp.Context('<code>')
        result, error = fpp.run('<stdin>' ,text, context)


        if error: print(error.as_string())
        elif result: 
            if len(result.elements) == 1:
                print(repr(result.elements[0]))
            else:
                print(repr(result))
            
            
def main():
    if len(sys.argv) == 1:
        run_prompt()
    else:
        filename = ' '.join(sys.argv[1:])
        run_file(filename)

if __name__ == "__main__":
    main()
