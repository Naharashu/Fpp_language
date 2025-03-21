from sys import *

def open_file(filename):
    data = open(filename, "r").read()
    data += "<EOF>"
    return data

tokens = []
num_stack = []
symbols = {}

def lex(filecontents):
    tok = ""
    state = 0
    string = ""
    varStarted = 0
    var = ""
    expr = ""
    n = ""
    isexpr = 0
    filecontents = list(filecontents)
    for char in filecontents:
        tok += char

        if tok == " ":
            if state == 0:
                tok = ""
            else:
                tok = " "

        elif tok == "\n" or tok == "<EOF>":
            if expr != "" and isexpr == 1:
                tokens.append("EXPR:" + expr)
                expr = ""
            elif expr != "" and isexpr == 0:
                tokens.append("NUM:" + expr)
                expr = ""
            elif var != "":
                tokens.append("VAR:" + var)
                var = ""
                varStarted = 0


            tok = ""

        elif tok.lower() == "write:":
            tokens.append("WRITE")
            tok = ""

        elif tok.lower() == "var" and state == 0:
            varStarted = 1
            tok = ""

        elif varStarted == 1 and tok.isalnum():
            var += tok
            tok = ""

        elif varStarted == 1 and tok == "=":
            tokens.append("VAR:" + var)
            var = ""
            varStarted = 0
            tokens.append("EQUALS")
            tok = ""

        elif varStarted == 1 and tok == " ":
            if tok == "<" or tok == ">":
                if var != "":
                    tokens.append("VAR:" + var)
                    var = ""
                    varStarted = 0
            tok = ""

        elif tok == "=" and state == 0:
            tokens.append("EQUALS")
            tok = ""

        
        elif tok == "0" or tok == "1" or tok == "2" or tok == "3" or tok == "4" or tok == "5" or tok == "6" or tok == "7" or tok == "8" or tok == "9":
            expr += tok
            tok = ""

        elif tok == "+" or tok == "-" or tok == "*" or tok == "/" or tok == "(" or tok == ")":
            isexpr = 1
            expr += tok
            tok = ""

        elif tok == "\"":
            if state == 0:
                state = 1
                tok = ""
            elif state == 1:
                tokens.append("STRING:" + string)
                string = ""
                state = 0
                tok = ""
        
        elif state == 1:
            string += tok
            tok = ""
    
    print("Tokens:", tokens)
    #return ''
    return tokens

def evalExpression(expr):
    return eval(expr)

def doPRINT(toPrint):
    if toPrint[0:6] == "STRING":
        toPrint = toPrint[7:]
        toPrint = toPrint[:-1]
    elif toPrint[0:3] == "NUM":
        toPrint = toPrint[4:]
    elif toPrint[0:4] == "EXPR":
        toPrint = evalExpression(toPrint[5:])
    elif toPrint[0:3] == "VAR":
        varname = toPrint[4:]
        toPrint = symbols[varname]
    else:
        print("Unknown type: " + toPrint)
    print(toPrint)

    print("doPRINT called with:", toPrint)

def doAssign(varname, varvalue):
    if varvalue[0:6] == "STRING":
        symbols[varname[4:]] = varvalue[7:]
    elif varvalue[0:3] == "NUM":
        symbols[varname[4:]] = int(varvalue[4:])
    elif varvalue[0:4] == "EXPR":
        symbols[varname[4:]] = evalExpression(varvalue[5:])
    else:
        print(f"Invalid assignment to {varname}: {varvalue}")

    print(f"Assigning {varvalue} to {varname}")

def getVar(varname):
    varname = varname[4:]
    if varname in symbols:
        return symbols[varname]
    else:
        return "Undeclared Variable Error!"

def parse(toks): 
    i = 0
    while(i < len(toks)): 
        if toks[i] + " " + toks[i+1][0:6] == "WRITE STRING" or toks[i] + " " + toks[i+1][0:3] == "WRITE NUM" or toks[i] + " " + toks[i+1][0:3] == "WRITE EXPR" or toks[i] + " " + toks[i+1] == "WRITE VAR":
            if toks[i+1][0:6] == "STRING":
                doPRINT(toks[i+1])
            elif toks[i+1][0:3] == "NUM":
                doPRINT(toks[i+1])
            elif toks[i+1][0:4] == "EXPR":
                doPRINT(toks[i+1])
            elif toks[i+1][0:4] == "VAR":
                doPRINT(getVar(toks[i+1]))
            i += 2

        elif toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:6] == "VAR EQUALS STRING" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:3] == "VAR EQUALS NUM" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:4] == "VAR EQUALS EXPR":
            doAssign(toks[i], toks[i+2])
            if toks[i+2][0:6] == "STRING":
                doAssign(toks[i], toks[i+2])
            elif toks[i+2][0:3] == "NUM":
                doAssign(toks[i], toks[i+2])
            elif toks[i+2][0:4] == "EXPR":
                doAssign(toks[i], evalExpression(toks[i+2][5:]))
            i += 3
    print("Parsing tokens:", toks)

    #print(symbols)


def run():
    data = open_file(argv[1])
    toks = lex(data)
    parse(toks)
    print("Parsing token:", toks)

run()