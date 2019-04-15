from __future__ import print_function
from coverdescriptor import CoverDescriptor
from covermatcher import CoverMatcher
import argparse
import glob
import csv
import cv2

ap = argparse.ArgumentParser()

ap.add_argument("-s", "--sift", type=int, default=0, help="whether or not SIFT should be used")

args = vars(ap.parse_args())

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

queryPaths = glob.glob("./querys/*.png")
for queryPath in queryPaths:
    queryImage = cv2.imread(queryPath)
    gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
    (queryKps, queryDescs) = cd.describe(gray)

    results = cm.search(queryKps, queryDescs)
    print(results)
    for item in results:
        if item[0] > 0.3:
            cv2.imshow("Query", queryImage)

    if len(results) == 0:
        print("I could not find a match for that cover!")
        #cv2.waitKey(0)

    else:
        for (i, (score, coverPath)) in enumerate(results):
            print(coverPath)
            (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
            if (score > 0.3):
                print("{}. {:.2f}% : {} - {}".format(i + 1, float(score * 100), author, title))
                result = cv2.imread(coverPath)
                cv2.imshow("Result", result)      

cv2.waitKey(0)


