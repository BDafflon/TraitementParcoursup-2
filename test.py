import re

line='''
De même avec le singulier- pluriel, masculin,  féminin.  Par exemple correct, correcte, corrects, correctes faut-il mettre les 4 ou c’est facile pour toi de demander de colorier tous les cas de figures (en gros rajouter -e -s -es)  à tous les mots clés (si le mot n’existe pas, ce n’est pas grave cela ne le coloriera pas…)
Est-ce qu’on ne peut faire colorier et compter que la partie bulletin du dossier ?
'''

match = re.findall(r"\bcorrect\w*\b",line)

print(match)