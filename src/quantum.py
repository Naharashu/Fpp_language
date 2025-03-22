import fpp

aaaaan = 0
while True:
    while aaaaan < 1:
        print("Welcome to Quantum. Its ide for F++. Current version is 0.1.0")
        print("Type 'exit' to exit")
        aaaaan += 1
    text = input("Quantum > ")
    if text == "exit":
        break
    result, error = fpp.run('<stdin>' ,text)

    if error: print(error.as_string())
    else: print(result)
