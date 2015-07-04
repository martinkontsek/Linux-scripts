################################################################
#                Kernel Updater for Xubuntu                    #
#                     by Martin Kontsek                        #
#                          2015                                #
#                                                              #
#  Requirements: Python 3 (3.4.3 tested)                       #
#                BeautifulSoup 4 (pip install beautifulsoup4)  #
################################################################

__author__ = 'Martin Kontsek'

from bs4 import BeautifulSoup
from subprocess import call
import urllib.request
import os

ARCH = "amd64"
#ARCH = "i386"
KERNEL_SHOW_COUNT = 20
PATH_TO_SAVE = "/tmp/KernelUpdater/"
url = "http://kernel.ubuntu.com/~kernel-ppa/mainline/"


def main():
    printWelcome()
    list = getDirs(url)
    printDir(list)
    print()
    val = input("Select item for installation: ")

    fileList = getFiles(val, list)
    toInstall = downloadFiles(fileList)
    install(toInstall)
    return

def printWelcome():
    print("*****************************************************")
    print("*           Kernel Updater for Xubuntu              *")
    print("*                by Martin Kontsek                  *")
    print("*                       2015                        *")
    print("*****************************************************")
    print()
    return

#prints list dir items
def printDir(paList):
    print("Available kernel versions: ")
    print()
    i = len(paList)-1
    j = i-KERNEL_SHOW_COUNT
    pos = 1
    for i in range(i,j,-1):
        print("(",pos,") ",paList[i])
        pos += 1
    return


#function for getting dir links
def getDirs(paUrl):
    list = []
    #get HTML document from URL
    content = urllib.request.urlopen(paUrl).read()

    soup = BeautifulSoup(content)

    for folder in soup.find_all('tr'):
        for link in folder.find_all('a'):
            pol = (link.get('href'))[:-1]
            list.append(pol)

    return list

def getFiles(paDirIndexFromEnd, paDirList):
    list = []

    item = paDirList[len(paDirList)-int(paDirIndexFromEnd)]
    urlPart = url + item + "/"

    #get HTML document from URL
    content = urllib.request.urlopen(urlPart).read()

    soup = BeautifulSoup(content)

    for folder in soup.find_all('tr'):
        for link in folder.find_all('a'):
            pol = link.get('href')
            if(pol.find("linux") != -1):
                if(pol.find("all") != -1):
                    list.append(urlPart + pol)
                if(pol.find("generic") != -1 and pol.find(ARCH) != -1):
                    list.append(urlPart + pol)
    return list

def downloadFile(paLink, paFilePath):
    u = urllib.request.urlopen(paLink)
    f = open(paFilePath, 'wb')
    file_name = paLink.split('/')[-1]
    meta = u.info()
    file_size = int(u.getheader('Content-Length'))
    print("Downloading file: ", file_name, "size: ", round(file_size/(1024*1024), 2),"MB")

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        #status = "[%3.2f%%]" % (file_size_dl * 100. / file_size)
        #print(status, end=" ")

    f.close()
    print("Download finished.")
    print()
    return

def downloadFiles(paLinkList):
    downloadedFiles = []
    if not os.path.exists(PATH_TO_SAVE):
        os.makedirs(PATH_TO_SAVE)
    else:
       for file in os.listdir(PATH_TO_SAVE):
           if os.path.isfile(file):
               os.unlink(file)

    for link in paLinkList:
        file_name = link.split('/')[-1]
        path = PATH_TO_SAVE+file_name
        downloadFile(link, path)
        downloadedFiles.append(path)
    return downloadedFiles

def install(paDownloadedFiles):
    print("Installing kernel...")
    for file in paDownloadedFiles:
        call(["sudo", "dpkg", "-i", file])
    return
main()
