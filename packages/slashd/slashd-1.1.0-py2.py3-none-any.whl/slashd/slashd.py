import sys
import socket
import random
sys.setrecursionlimit(2147483647)
import os.path
import os
variables = ["slsh", "opbr", "clbr", "coln", "addr"]
variabledata = ["/", "(", ")", ":", ""]
from decimal import Decimal
from functools import cache

def reset(line):
  global mainsect
  global subsect
  mainsect = ""
  subsect = ""
  return line+1

def parse(text, start, chars):
  i = start
  returnVal = ""
  while text[i] not in chars:
    returnVal += text[i]
    i += 1
  return returnVal

@cache
def operatin(one, two, operation, line):
  if operation[0] != '"' and operation != "=":
    try:
      Decimal(one)
    except:
      print("Error on Line "+str(line+1)+ ": expected number")
      quit()
  if operation == '"*' or operation == '"=' or operation == '"-':
    try:
      Decimal(two)
    except:
      print("Error on Line "+str(line+1)+ ": expected number")
      quit()
  if operation == "*":
    return Decimal(one) * Decimal(two)
  if operation == "+":
    return Decimal(one) + Decimal(two)
  if operation == "-":
    return Decimal(one) - Decimal(two)
  if operation == "|":
    return Decimal(one) / Decimal(two)
  if operation == "%":
    return Decimal(one) % Decimal(two)
  if operation == "^":
    return Decimal(one) ** Decimal(two)
  if operation == ">":
    return Decimal(one) > Decimal(two)
  if operation == "<":
    return Decimal(one) < Decimal(two)
  if operation == "=":
    return str(one) == two
  if operation == ">=":
    return Decimal(one) >= Decimal(two)
  if operation == "<=":
    return Decimal(one) <= Decimal(two)
  if operation == "><":
    return Decimal(one) != Decimal(two)
  if operation == '"+':
    return one + two
  if operation == '"*':
    if Decimal(two) % 1 != 0 or Decimal(two) < 0:
      print("Error on Line "+str(line+1)+ ": expected positive integer")
      quit()
    return one * int(two)
  if operation == '"=':
    if Decimal(two) % 1 != 0 or Decimal(two) < 0:
      print("Error on Line "+str(line+1)+ ": expected positive integer")
      quit()
    return one[int(two)]
  if operation == '"-':
    if Decimal(two) % 1 != 0 or Decimal(two) < 0:
      print("Error on Line "+str(line+1)+ ": expected positive integer")
      quit()
    temp = int(two)
    return one[0:temp]+one[temp+1::]
  if operation == '<>':
    return random.randint(int(one), int(two))
  print("Error on Line "+str(line+1)+": operation not found")
  quit()

charss = ["*", "+", "-", "|", "%", "^", ">", "<", "=", '"']
charsss = ["=", "<", "+", "*", ">", "-"]
def math(line, start, linenum):
  global charss
  global charsss
  one = 0
  two = 0
  operation = ""
  if line[0] == "-":
    text = "-" + parse(line, 1, charss)
  else:
    text = parse(line, start, charss)
  leng = len(text)
  if text[0] == ":":
    subsect = text[1:]
    if not subsect in variables:
        print("Error on Line "+str(linenum+1)+": variable not declared")
    one = variabledata[variables.index(subsect)]
  else:
    one = text
  text = line[start+leng]
  if text not in charss:
    print("Error on Line "+str(linenum+1)+": operation not found")
    quit()
  operation = text
  text = line[start+leng+1]
  if text in charsss:
    operation += text
    leng += 1
  text = parse(line + "¬", start+1+leng, "¬")
  if text[0] == ":":
    subsect = text[1:]
    if not subsect in variables:
      print("Error on Line "+str(linenum+1)+": variable not declared")
      quit()
    two = variabledata[variables.index(subsect)]
  else:
    two = text
  return operatin(one, two, operation, linenum)

def run(filename):
  cod = open(filename, "r")
  code = cod.readlines()
  del cod
  global mainsect
  global subsect
  line = reset(-1)
  length = len(code)
  while line < length:
    try:
      mainsect = parse(code[line], 0, list("/"))
    except:
      mainsect == ""
    if mainsect == "let":
      subsect = parse(code[line], 4, list("/"))
      if subsect in variables:
        variablenum = variables.index(subsect)
      else:
        variables.append(subsect)
        variabledata.append("")
        variablenum = variables.index(subsect)
      subsect = parse(code[line], 5+len(subsect), list("/"))
      if subsect[0] == "(" and subsect[-1] == ")":
          variabledata[variablenum] = math(subsect[1:-1], 0, line)
      else:
          if str(subsect)[0] == ":":
            subsect = subsect[1:]
            if not subsect in variables:
              print("Error on Line "+str(line+1)+": variable not declared")
              quit()
            subsect = variabledata[variables.index(subsect)]
          variabledata[variablenum] = subsect
      line = reset(line)
      continue
    elif mainsect == "out":
      subsect = parse(code[line], 4, list("/"))
      if str(subsect)[0] == ":":
        subsect = subsect[1:]
        if not subsect in variables:
          print("Error on Line "+str(line+1)+": variable not declared")
          quit()
        subsect = variabledata[variables.index(subsect)]
      print(subsect)
      line = reset(line)
      continue
    elif mainsect == "go":
      subsect = parse(code[line], 3, list("/"))
      if str(subsect)[0] == ":":
        subsect = subsect[1:]
        if not subsect in variables:
          print("Error on Line "+str(line+1)+": variable not declared")
          quit()
        subsect = variabledata[variables.index(subsect)]
      try:
        int(subsect)
      except:
        print("Error on Line "+str(line+1)+": expected int")
        quit()
      if int(subsect) < 1:
        print("Error on Line "+str(line+1)+": expected value of at least 1")
        quit()
      templine = int(subsect)-1
      if templine >= length:
        print("Error on Line "+str(line+1)+": line doesn't exist")
      line = templine - 1
      line = reset(line)
      continue
    elif mainsect == "del":
      subsect = parse(code[line], 4, list("/"))
      if subsect in variables:
        variablenum = variables.index(subsect)
      else:
          print("Error on Line"+str(line+1)+": variable not declared")
      variables.pop(variablenum)
      variabledata.pop(variablenum)
      line = reset(line)
      continue
    elif mainsect == "if":
      subsect = parse(code[line], 3, list("/"))
      leng = len(subsect)
      if subsect[0] == "(" and subsect[-1] == ")":
          subsect = math(subsect[1:-1], 0, line)
      try:
        subsect = bool(subsect)
      except:
        print("Error on Line"+str(line+1)+": expected boolean value")
        quit()
      if subsect == False:
        subsect = parse(code[line], 4+leng, list("/"))
        if str(subsect)[0] == ":":
          subsect = subsect[1:]
          if not subsect in variables:
            print("Error on Line "+str(line+1)+": variable not declared")
            quit()
          subsect = variabledata[variables.index(subsect)]
        try:
          int(subsect)
        except:
          print("Error on Line "+str(line+1)+": expected int")
          quit()
        if int(subsect) < 1:
          print("Error on Line "+str(line+1)+": expected value of at least 1")
          quit()
        templine = int(subsect)-1
        if templine >= length:
          print("Error on Line "+str(line+1)+": line doesn't exist")
          quit()
        line = templine - 1
      line = reset(line)
      continue
    elif mainsect == "in":
      subsect = parse(code[line], 3, list("/"))
      if not subsect in variables:
          print("Error on Line "+str(line+1)+": variable not declared")
          quit()
      variablenum = variables.index(subsect)
      subsect = parse(code[line], 4+len(subsect), list("/"))
      variabledata[variablenum] = input(subsect)
      line = reset(line)
      continue
    elif mainsect == "run":
      subsect = parse(code[line], 4, list("/"))
      if subsect[0] == ":":
        subsect = subsect[1:]
        if not subsect in variables:
          print("Error on Line "+str(line+1)+": variable not declared")
          quit()
        subsect = variabledata[variables.index(subsect)]
      if os.path.isfile(subsect) == False:
        print("Error on Line "+str(line+1)+": file not found")
        quit()
      run(subsect)
      line = reset(line)
      continue
    elif mainsect == "clear":
      os.system("clear")
      line = reset(line)
      continue
    elif mainsect == "":
      line = reset(line)
      continue
    elif mainsect == "createsock":
      sock = socket.socket()
      line = reset(line)
      continue
    elif mainsect == "bindsock":
      ip = parse(code[line], 9, list("/"))
      port = int(parse(code[line], 10+len(ip), list("/")))
      sock.bind((ip, port))
      line = reset(line)
      continue
    elif mainsect == "listensock":
      connectionnum = int(parse(code[line], 11, list("/")))
      sock.listen(connectionnum)
      line = reset(line)
      continue
    elif mainsect == "acceptconnect":
      c, addr = sock.accept()
      variabledata[variables.index("addr")] = addr
      line = reset(line)
      continue
    elif mainsect == "sendsock":
      subsect = parse(code[line], 9, list("/"))
      c.send(subsect.encode("UTF-8"))
      line = reset(line)
      continue
    elif mainsect == "closeconnect":
      c.close()
      line = reset(line)
      continue
    elif mainsect == "closesock":
      sock.close()
      line = reset(line)
      continue
    elif mainsect == "recvsock":
      subsect = parse(code[line], 9, list("/"))
      if not subsect in variables:
          print("Error on Line "+str(line+1)+": variable not declared")
          quit()
      variablenum = variables.index(subsect)
      subsect = parse(code[line], 10+len(subsect), list("/"))
      variabledata[variablenum] = sock.recv(int(subsect)).decode()
      line = reset(line)
      continue
    elif mainsect == "sockconnect":
      ip = parse(code[line], 12, list("/"))
      port = int(parse(code[line], 13+len(ip), list("/")))
      sock.connect((ip, port))
      line = reset(line)
      continue
    else:
      print("Error on Line "+str(line+1)+": command unknown")
      quit()