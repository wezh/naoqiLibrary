exit_flag = False

while True:

    text = raw_input("Input something: ")

    print (text)
    while True:
        if "First" not in text:
            print ("First not in text")
            exit_flag = True
            break
        else:
            print ("First yes!")
    if exit_flag:
        break