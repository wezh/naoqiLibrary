from coverdescriptor_naoqi import CoverDescriptor
from covermatcher_naoqi import CoverMatcher
import argparse
import glob
import csv
import cv2
import paramiko
import os
import datetime

ap = argparse.ArgumentParser()

# ap.add_argument("-q", "--query", required=True, help="path to the query book cover")

args = vars(ap.parse_args())

user = "nao"
passwd = "nimdA"
IP = "192.168.1.145"
photoPath = "/home/nao/Library/queryTemp/"
localPath = "/Users/wenhao/PycharmProjects/Library/querys/"

db = {}

for l in csv.reader(open("books.csv")):
    db[l[0]] = l[1:]

cd = CoverDescriptor()
cm = CoverMatcher(cd, glob.glob("cover" + "/*.png"))

try:
    t = paramiko.Transport((IP, 22))
    t.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(t)
    files = sftp.listdir(photoPath)
    for f in files:
        print ('')
        print ('##############################################')
        print ('Beginning to download file from %s %s' % (IP, datetime.datetime.now()))
        print ('Downloading file:', os.path.join(photoPath, f))
        sftp.get(os.path.join(photoPath, f), os.path.join(localPath, f))
        print ('Download file success %s' % datetime.datetime.now())
        print ('')
        print ('##############################################')
    t.close()
except Exception:
    print ("connect error!")

queryImage = cv2.imread("query001.png")
gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
(queryKps, queryDescs) = cd.describe(gray)

results = cm.search(queryKps, queryDescs)

# cv2.imshow("Query", queryImage)

if len(results) == 0:
    print "I could not find a match for that cover"
    # cv2.waitKey(0)

else:
    for (i, (score, coverPath)) in enumerate(results):
        (author, title) = db[coverPath[coverPath.rfind("/") + 1:]]
        print "%d %.2f%% : %s - %s" % (i + 1, score * 100, author, title)
        if i == 0:
            break
        # result = cv2.imread(coverPath)
        # cv2.imshow("Result", result)
        # cv2.waitKey(0)
