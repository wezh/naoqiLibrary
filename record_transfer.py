from ftplib import FTP
import paramiko

class Transfer_Recorded_Audio():

    def ftpconnect(host, username, password):
        ftp = FTP(host="192.168.1.105", user="nao", passwd="nimdA")
        ftp.connect(host, 21)
        ftp.login(username, password)

    def downloadRecordedAudioFile(ftp, remotepath, localpath):
        bufsize = 1024
        fp = open(localpath, 'wb')
        ftp.retrbinary("RETR " + remotepath, fp.write, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
    
    if __name__ == "__main__":
