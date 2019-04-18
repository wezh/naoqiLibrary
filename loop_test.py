import cv2
import argparse
import csv
import glob
from coverdescriptor import CoverDescriptor
from covermatcher import CoverMatcher

ap = argparse.ArgumentParser()

exit_flag = False

ap.add_argument("-s", "--sift", type=int, default=0, help="whether or not SIFT should be used")

args = vars(ap.parse_args())

checkbox_1 = ('borrow', 'take')
checkbox_2 = ('return')
checkbox_3 = ('no')

while True:
    print ('what can I do for you')

    while True:

        keyboard = raw_input("Input: ")
        result = keyboard in checkbox_1
        if result:
            print('keyword: ' + keyboard + 'GET!')
            print ('Sure! I am going to take a picture of the book you would like to borrow, please put the book cover in front of my eyes')

            while True:
                print ('Photo capturing')
                print ("Finished")
                print('transfer photo correctly!')
                print('###################################bo###########')
                # Book Cover Matching Porcess
                db = {}

                for l in csv.reader(open("books.csv")):
                    db[l[0]] = l[1:]

                useSIFT = args["sift"] > 0
                useHamming = args["sift"] == 0
                ratio = 0.7
                minMatches = 40

                if useSIFT:
                    minMatches = 50
                cd = CoverDescriptor(useSIFT=useSIFT)
                cm = CoverMatcher(cd, glob.glob("./cover/*.png"),
                                  ratio=ratio, minMatches=minMatches, useHamming=useHamming)

                queryImage = cv2.imread('./querys/query.png')
                gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
                (queryKps, queryDescs) = cd.describe(gray)

                results = cm.search(queryKps, queryDescs)
                print (results)

                if len(results) == 0:
                    print('I could not find a match for that cover! Do you want me to take a photo again?')

                    keyboard = raw_input('Input: ')

                    print('User speaking: ' + answer)
                    print('##############################################')

                    if 'no' not in keyboard:
                        print ("Sure!")
                    else:
                        print('OK. Anything else I can do for you?')
                        keyboard = raw_input('Input: ')
                        print('User speaking: ' + keyboard)
                        if 'no' not in answer:
                            print ('Sure!')
                            exit_flag = True
                            break
                    if exit_flag:
                        break
                else:
                    for (i, (score, coverPath)) in enumerate(results):
                        if (score > 0.5):
                            (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
                            print('{}. {:.2f}% : {} - {}'.format(i + 1, score * 100, author, title))
                            result = cv2.imread(coverPath)
                            cv2.imshow('Query', queryImage)
                            cv2.imshow('Result', result)
                            print('##############################################')
                            print('Is this one the correct book you would like to borrow?')
                            cv2.waitKey(0)
                            recordAudioFromNao()
                            answer = SpeechTransferToText()
                            keyboard = raw_input('Input: ')
                            if "yes" in answer:
                                tts.say("Prefect! I added this one to your account! Anything else I can do for you?")
                                numberOfBorrowedBooks += 1
                                recordAudioFromNao()
                                answer = SpeechTransferToText(local_recordingFile)
                                if "yes" in answer:
                                    tts.say("Ok!")
                                    break
                                else:
                                    exit_flag = True
                                    break
                                if exit_flag:
                                    break

                                break
                            else:
                                tts.say("Ok, Let me take photo again!")
                        else:
                            print('Matching Ratio is too low to identify. Do you want me to take a photo again?')
                            print('Matching Ratio is too low to identify. Do you want me to take a photo again?')
                            print('##############################################')

                            keyboard = raw_input('Input: ')

                            if 'no' not in keyboard:
                                print('Sure!')
                            else:
                                print('OK. Anything else I can do for you?')

                                keyboard = raw_input('Input: ')
                                if 'no' not in keyboard:
                                    print('OK')
                                    break
                                else:
                                    exit_flag = True
                                    break
                            if exit_flag:
                                break
                        if exit_flag:
                            break

    #
    # text = raw_input("Input something: ")
    #
    # print (text)
    # while True:
    #     if "First" not in text:
    #         print ("First not in text")
    #         exit_flag = True
    #         break
    #     else:
    #         print ("First yes!")
    # if exit_flag:
    #     break