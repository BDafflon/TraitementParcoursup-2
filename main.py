import fileinput
import os
import re
import subprocess
from os import listdir
from os.path import isfile, join
import chardet
import numpy as np
import json
from string import digits

def parseDir(dir,export):
    onlyfiles = [{'file':f} for f in listdir(dir) if join(dir,f).lower().endswith('pdf') and isfile(join(dir, f))]
    onlyfilesHTML = [{'file': f} for f in listdir(export) if join(export, f).lower().endswith('html') and isfile(join(export, f))]
    return onlyfiles,onlyfilesHTML

def convert(pathDir,pathHTML,files):
    dir_existe = os.path.isdir(pathHTML)

    if not dir_existe:
        os.mkdir(pathHTML)
    success=[]
    error = []
    for file in files:
        f=file['file']
        print("Convert ",join(pathHTML,f[:-3])+"html")
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
        print("Coloration ", join(path,f))
        file = open(join(path,f),mode='r',encoding="utf8")
        doc = file.read()

        content = doc.split('<body>')[1]

        head = doc.split('<body>')[0]
        head = re.sub(r'<style type="text/css">', css, head,1)
        apreciation = content.split('ciations des professeurs :')
        if len(apreciation)>1:
            buletin = content.split('ciations des professeurs :')[0]
            lettre = 'ciations des professeurs :' + 'ciations des professeurs :'.join(content.split('ciations des professeurs :')[1:])
        else:
            buletin = content.split('Projet de formation motiv')[0]
            lettre = 'Projet de formation motiv' + 'Projet de formation motiv'.join(content.split('Projet de formation motiv')[1:])


        buletin = buletin.replace("&apos;","'")


        success[i]['word']=[]
        success[i]['pos'] = 0
        success[i]['neg']=0
        for n in neg:

            find = re.findall(r"\b"+n[0]+r"\b", buletin ,flags=re.IGNORECASE)
            success[i]['word'].append([n[0],len(find)])
            for fi in find:
                match = re.subn(r'\b'+fi+r'\b', '<span class="neg-'+str(n[1])+'">'+fi+'</span>', buletin,flags=re.IGNORECASE)
                buletin = match[0]
                success[i]['neg']+=n[1]


        for n in pos:

            find = re.findall(r"\b"+n[0]+r"\b", buletin ,flags=re.IGNORECASE)
            success[i]['word'].append([n[0],len(find)])
            for fi in find:
                match = re.subn(r'\b'+fi+r'\b', '<span class="pos-'+str(n[1])+'">'+fi+'</span>', buletin,flags=re.IGNORECASE)
                buletin = match[0]
                success[i]['pos'] += n[1]

        file.close()
        file = open(join(path,f), mode='w',encoding="utf8")
        data = head+'<body>'+buletin+lettre
        file.write(data)
        file.close()
    return success

def log(data,path,historique):
    csv="file;Rep1;Rep2;Rep3;Positif;Negatif;"

    for w in data[0]['word']:
        csv+=w[0]+";"

    csv+="\n"

    for d in data:
        num = re.search('-N(.*).html', d['file'], re.IGNORECASE)
        if num :
            csv +=num.group(1)+";"
        else:
            csv+=d['file']+";"

        find=False
        for h in historique:
            if h[0] in d['file']:
                csv +=h[1]+";"+h[2]+";"+h[3]+";"
                find=True
        if not find:
            csv += ";;;"

        csv += str(d['pos']) + ";"
        csv += str(d['neg']) + ";"
        for w in d['word']:
            csv+=str(w[1])+";"
        csv += "\n"

    f = open(join(path,"indicateur.csv"), mode='w',encoding="utf8")
    f.write(csv)
    f.close()

def datacleaning(path,file):
    fileData = open(join(path,file), 'r')
    data = [f.split(";")[1:] for f in fileData.read().split('\n')[1:-1]]
    dataC=[]
    for d in data:
        if d[0]=="Oui" or d[2]=='Oui':
            d=[1]+d[3:-1]
        else:
            d = [0] + d[3:-1]


        d = [int(i) for i in d]
        N=100

        resD = d


        dataC+=[resD]

    csv="res;pos;neg;"
    for i in range(0,N):
        csv+="mot"+str(i)+";"

    csv +='\n'
    for l in dataC:
        csv+='; '.join(map(str, l)) + '\n'
    f = open(join(path, "dataCleaning.csv"), mode='w', encoding="utf8")
    f.write(csv)
    f.close()


def createVocable(path,historique):
    print("Creation corpus")
    corpusPositif=""
    corpusNegatif=""
    onlyfilesHTML = [{'file': f} for f in listdir(path) if join(path, f).lower().endswith('html') and isfile(join(path, f))]
    print("nombre de fichier ",len(onlyfilesHTML))
    fullBuletinTab = []
    tags=[" dossier ° dut génie mécanique page " ," dossier n ° dut génie mécanique page ","dossier n ° dut génie mécanique page"," : matière trimestre ème trimestre ème trimestre "," bas"," dossier n° - dut - génie mécanique page ", "projet formation motiv"," : matière trimestre ème trimestre ",]

    for i,file in enumerate(onlyfilesHTML):
        if i>10000:
            break
        f=file["file"]


        print(f)
        file = open(join(path,f),mode='r',encoding="utf8")
        doc = file.read()

        content = doc.split('<body>')[1]

        buletin=""
        buletin = "Bulletins scolaires de l'année".join(content.split("Bulletins scolaires de l'année")[1:])

        buletin = buletin.split("Projet de formation")[0]

        buletin = buletin.split("Appréciations des professeurs :")[0]

        buletin = buletin.lower()

        buletin = buletin.replace("&apos;"," ")
        buletin = buletin.replace("'", " ")
        buletin = buletin.replace("\.", " ")
        buletin = buletin.replace("</div", " . </div")

        buletin = cleanhtml(buletin)


        buletin = removeStopwords(buletin, stopwords)

        buletin = removeChar(buletin, ["\+","\(","\)","\*", ',',"/","_",'-'])

        buletinTab = buletin.split("bulletins scolaires année")
        print(len(buletinTab))

        buletinTabSplit=[]
        for b in buletinTab:
            dictAnnee={}

            annee = [int(i) for i in b.split(" : ")[0].split(" ") if i !=""]
            dictAnnee["annee"]=annee

            b = re.sub('\w+\d+ \d+\w+',"&&&",b.lower())
            remove_digits = b.maketrans('', '', digits)
            b = b.translate(remove_digits)
            b = re.sub(' +', ' ', b.lower())
            b = re.sub('\n', '.', b.lower())

            findall = re.findall("(\. [^\.]+? &&&)",b)
            for fi in findall:
                if fi ==". &&& &&&":
                    continue
                print(fi)
                b=re.sub(fi,"|||"+fi[1:],b)


            b = re.sub("& &","",b)

            b = re.sub("&&+","&&&",b)


            dictAnnee["data"] = [ {'matiere':i.split("&&&")[0].replace('|',''),'commentaire':[x for x in ''.join(i.split("&&&")[1:]).split('.') if x not in tags and x!="" and x!=" "]} for i in b.split("|||") if i!=" " and i not in tags and i!="" and i[1]!="&"]
            buletinTabSplit.append(dictAnnee)

        for h in historique:
            if h[0] in f :
                if h[1]=='Oui' or h[3]=='Oui':
                    fullBuletinTab.append({'file':f,'data':buletinTabSplit,'results':'Oui'})
                else:
                    fullBuletinTab.append({'file':f,'data':buletinTabSplit,'results':'Non'})


    with open('data.txt', 'w',encoding="utf8") as outfile:
        json.dump(fullBuletinTab, outfile,ensure_ascii=False)

    print("fin corpus")
    return join(path, "corpus.txt")

def removeChar(text,rm):
    for w in rm:
        text = re.sub(w, ' ', text.lower())
    text = re.sub(' +', ' ', text.lower())
    return text

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, ' ', raw_html)
  cleantext = re.sub(' +', ' ', cleantext)

  return cleantext

def removeStopwords(text,words):
    for w in words:
        text = re.sub(r'\b'+w.lower()+r'\b', ' ', text.lower())
    text = re.sub(' +', ' ', text)
    return text



if __name__ == '__main__':

    pathDir = "dossier"
    pathHTML = "export"

    negFile = open('input/negatif.txt', 'r')
    posFile = open('input/positif.txt', 'r')
    neutreFile = open('input/blue.txt','r')
    historiqueFile = open('input/historique.csv','r')
    stopwordFile = open('input/stopword.txt','r')

    historique = [f.split(";") for f in historiqueFile.read().split('\n')]
    neg = [[f.split('\t')[0], int(f.split("\t")[1])] for f in negFile.readlines()]
    pos = [[f.split('\t')[0], int(f.split("\t")[1])] for f in posFile.readlines()]
    neutre = [[f.split('\t')[0], int(f.split("\t")[1])] for f in neutreFile.readlines()]
    stopwords = [f for f in stopwordFile.read().split('\n')]


    #files,htmls = parseDir(pathDir,pathHTML)

    #print(historique)
    #success,error=convert(pathDir,pathHTML,files)
    #success=process(neg,pos,neutre,htmls,pathHTML)
    #log(success,pathHTML,historique)
    corpusPath = createVocable(pathHTML,historique)
    #datacleaning(pathHTML,'indicateur.csv')