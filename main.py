import fileinput
import os
import re
import subprocess
from os import listdir
from os.path import isfile, join


def parseDir(dir):
    onlyfiles = [f for f in listdir(dir) if join(dir,f).lower().endswith('pdf') and isfile(join(dir, f))]
    return onlyfiles

def convert(pathDir,pathHTML,files):
    dir_existe = os.path.isdir(pathHTML)

    if not dir_existe:
        os.mkdir(pathHTML)
    success=[]
    error = []
    for f in files:
        file_exists = os.path.isfile(join(pathHTML,f[:-3])+"html")
        if file_exists:
            success.append(f[:-3] + "html")
            continue
        cmd_line = "./lib/pdf2htmlEX.exe "+join(pathDir,f)+" "+join(pathHTML,f[:-3])+"html"
        res = subprocess.run(cmd_line, capture_output=True)
        if res.returncode != 0:
             error.append([f])
        else:
            success.append(f[:-3]+"html")
    return success,error

def process(neg,pos,neutre,success,path):
    #add CSS
    css=r'''<style type="text/css">
    .neg-5{background: rgb(255, 0, 0)}
    .neg-4{background: rgb(255, 60, 60)}
    .neg-3{background: rgb(255, 120, 120)}
    .neg-2{background: rgb(255, 180, 180)}
    .neg-1{background: rgb(255, 220, 220)}
    .pos-5{background: rgb(0, 255, 0)}
    .pos-4{background: rgb(60, 255, 60)}
    .pos-3{background: rgb(120, 255, 120)}
    .pos-2{background: rgb(180, 255, 180)}
    .pos-1{background: rgb(220, 255, 220)}
    '''

    for f in success:
        print(join(path,f))
        file = open(join(path,f), 'r')
        doc = file.read()

        content = doc.split('<body>')[1]

        head = doc.split('<body>')[0]
        head = re.sub(r'<style type="text/css">', css, head)


        buletin = content.split('Projet de formation motivé')[0]
        print(buletin)
        lettre = 'Projet de formation motivé'+'Projet de formation motivé'.join(content.split('Projet de formation motivé')[1:])

        for i,n in enumerate(neg):

            print(n)
            find = re.findall(r"\b"+n[0]+r"\b", buletin ,flags=re.IGNORECASE)

            for fi in find:
                match = re.subn(r'\b'+fi+r'\b', '<span class="neg-'+str(n[1])+'">'+fi+'</span>', buletin,flags=re.IGNORECASE)
                buletin = match[0]
                print(n,match[1])

        for i,n in enumerate(pos):

            print(n)
            find = re.findall(r"\b"+n[0]+r"\b", buletin ,flags=re.IGNORECASE)

            for fi in find:
                match = re.subn(r'\b'+fi+r'\b', '<span class="pos-'+str(n[1])+'">'+fi+'</span>', buletin,flags=re.IGNORECASE)
                buletin = match[0]
                print(fi,match[1])

        file.close()
        file = open(join(path,f), 'wt')
        file.write(head+'<body>'+buletin+lettre)
        file.close()


if __name__ == '__main__':

    pathDir = "dossier"
    pathHTML = "export"

    negFile = open('input/negatif.txt', 'r')
    posFile = open('input/positif.txt', 'r')
    neutreFile = open('input/blue.txt','r')

    neg = [[f.split('\t')[0], int(f.split("\t")[1])] for f in negFile.readlines()]
    pos = [[f.split('\t')[0], int(f.split("\t")[1])] for f in posFile.readlines()]
    neutre = [[f.split('\t')[0], int(f.split("\t")[1])] for f in neutreFile.readlines()]

    files = parseDir(pathDir)

    success,error=convert(pathDir,pathHTML,files)
    process(neg,pos,neutre,success,pathHTML)
