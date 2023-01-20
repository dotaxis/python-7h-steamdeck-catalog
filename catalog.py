import os
import re
import xml.etree.ElementTree as ET
import requests
from py7zr import SevenZipFile
from requests import get
from PyQt5.QtWidgets import *
from PyQt5 import uic
import gdown

class MyGUI(QMainWindow):
    
    def __init__(self):
        mods = []

        super(MyGUI, self).__init__()
        uic.loadUi("g.ui", self)
        self.show()



        def readModsDir():
            if os.path.exists('directory.txt'):
                modsDir = open('directory.txt', 'r').read()
                self.txtModFolder.setText(modsDir)
                listModsInstalled(modsDir)

        def setModsDir():
            modsDir = self.txtModFolder.text();
            with open('directory.txt', 'w') as f:
                f.write(modsDir)
                listModsInstalled(modsDir)

        def listModsAvailable():
            #parseMods('sega.xml')
            parseMods('catalog.xml')
            for i in range(0, len(mods) - 1):
                #print(f"{i}: {mods[i][0]}\nLink: {mods[i][1]}")
                self.listAvailableMods.addItem(mods[i][0])

        def listModsInstalled(path):
            self.listInstalledMods.clear()
            #print(f"Path: {path}")
            if os.path.exists(path):
                for file in os.scandir(path):
                    if file.is_dir() or file.is_file():
                        if  file.name != "temp":
                            self.listInstalledMods.addItem(file.name)


        def parseMods(catalog):
            tree = ET.parse(catalog)
            modstree = tree.getroot().find('Mods')
            for mod in modstree.findall('Mod'):
                name = mod.find('Name').text
                url = mod.find('LatestVersion').find('Link').text
                url = url.replace("iros://Url/https$", "https://")
                url = url.replace("iros://Url/http$", "http://")
                url = url.replace("iros://Url/", "")
                mods.append([name, url])
                mods.sort();

        def installMod():
            selectedMod = self.listAvailableMods.currentItem().text()
            #print(selectedMod)
            url = mods[find_in_list_of_list(mods, selectedMod)][1]
            selectedMod = selectedMod.replace("/",  "-")
            print("Url: " + url)
            modsDir = f"{self.txtModFolder.text()}"
            if "iros://GDrive/" not in url:
                if ".iro" in url:
                    print(f"{modsDir}/{selectedMod}.iro")
                    download(url, f"{modsDir}/{selectedMod}.iro")
                else:
                    download(url, f"{modsDir}/{selectedMod}.7z")
                    try2extract(modsDir, selectedMod)
            else:
                id = url.replace("iros://GDrive/", "")
                out = f"{modsDir}/{selectedMod}.7z"
                try:
                    gdown.download(id=id, output=out, quiet=False)
                except:
                    gdownload(id, out)
                try2extract(modsDir, selectedMod)

            listModsInstalled(modsDir)

        listModsAvailable()
        readModsDir()
        self.btnModFolderSave.clicked.connect(setModsDir)
        self.btnInstallMod.clicked.connect(installMod)

def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)

def try2extract(path, selectedMod):
    try:
        SevenZipFile(f"{path}/{selectedMod}.7z").extractall(f"{path}/{selectedMod}/")
        os.remove(f"{path}/{selectedMod}.7z")
    except:
        print("not a 7z archive")
        os.rename(f"{path}/{selectedMod}.7z", f"{path}/{selectedMod}.iro")

def find_in_list_of_list(mylist, char):
    for sub_list in mylist:
        if char in sub_list:
            return mylist.index(sub_list)
    raise ValueError("'{char}' is not in list".format(char = char))

def filename(id):
    url = 'https://drive.google.com/uc?export=download&id='+id
    response = requests.get(url)
    header = response.headers['Content-Disposition']
    file_name = re.search(r'filename="(.*)"', header).group(1)
    print("Gotcha ! File Name is --> "+file_name)
    return file_name

def gdownload(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()
    
if __name__ == '__main__':
    main()
