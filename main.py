import fileinput
import os
import re
import subprocess
from os import listdir
from os.path import isfile, join


def parseDir(dir):
    onlyfiles = [{'file':f} for f in listdir(dir) if join(dir,f).lower().endswith('pdf') and isfile(join(dir, f))]
    return onlyfiles

def convert(pathDir,pathHTML,files):
    dir_existe = os.path.isdir(pathHTML)

    if not dir_existe:
        os.mkdir(pathHTML)
    success=[]
    error = []
    for file in files:
        f=file['file']
        file_exists = os.path.isfile(join(pathHTML,f[:-3])+"html")
        if file_exists:
            success.append({'file':f[:-3] + "html"})
            continue
        cmd_line = "./lib/pdf2htmlEX.exe "+join(pathDir,f)+" "+join(pathHTML,f[:-3])+"html"
        res = subprocess.run(cmd_line, capture_output=True)
        if res.returncode != 0:
             error.append({'file':f})
        else:
            success.append({'file':f[:-3] + "html"})
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
    for i,file in enumerate(success):
        f=file["file"]
        file = open(join(path,f),mode='r')
        doc = file.read()

        content = doc.split('<body>')[1]

        head = doc.split('<body>')[0]
        head = re.sub(r'<style type="text/css">', css, head,1)
        buletin = content.split('Projet de formation motiv')[0]
        lettre = 'Projet de formation motiv'+'Projet de formation motiv'.join(content.split('Projet de formation motiv')[1:])

        success[i]['word']=[]
        for n in neg:

            find = re.findall(r"\b"+n[0]+r"\b", buletin ,flags=re.IGNORECASE)
            success[i]['word'].append([n[0],len(find)])
            for fi in find:
                match = re.subn(r'\b'+fi+r'\b', '<span class="neg-'+str(n[1])+'">'+fi+'</span>', buletin,flags=re.IGNORECASE)
                buletin = match[0]


        for n in pos:

            find = re.findall(r"\b"+n[0]+r"\b", buletin ,flags=re.IGNORECASE)
            success[i]['word'].append([n[0],len(find)])
            for fi in find:
                match = re.subn(r'\b'+fi+r'\b', '<span class="pos-'+str(n[1])+'">'+fi+'</span>', buletin,flags=re.IGNORECASE)
                buletin = match[0]


        file.close()
        file = open(join(path,f), 'w')
        data = head+'<body>'+buletin+lettre
        file.write(data)
        file.close()
    return success


def log(data,path):
    csv=";"

    for w in data[0]['word']:
        csv+=w[0]+";"

    csv+="\n"
    for d in data:
        print(d)
        csv+=d['file']+";"
        for w in d['word']:
            csv+=str(w[1])+";"
        csv += "\n"
    print(csv+"\n")
    f = open(join(path,"indicateur.csv"), "w")
    f.write(csv)
    f.close()



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
    success=process(neg,pos,neutre,success,pathHTML)
    log(success,pathHTML)
