import pandas as pd
from new_mrecommender import mdf,mcosine_sim
import sqlite3
import numpy as np

def return_similar_to_mfavourite(list1):
    similar_mangas = np.array([0*x for x in range(len(mcosine_sim[0]))])
    similar_mangas = similar_mangas.astype('float64') 
    for manga in list1:
        # print(manga[1])
        manga_ind = mdf[mdf.Name == manga[1]]["Index"].values[0]
        similarities = mcosine_sim[manga_ind]
        for e in range(len(similarities)):
            similar_mangas[e] = similar_mangas[e]+similarities[e]

    similar_mangas = list(enumerate(similar_mangas))
    sorted_similar_mangas = sorted(similar_mangas,key=lambda x:x[1],reverse=True)[:10]
    # print(sorted_similar_mangas)
    ret = []
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for manga in sorted_similar_mangas:
        res = cur.execute("SELECT * FROM mangalist WHERE name = ?", [mdf[mdf.Index == manga[0]]["Name"].values[0]])
        rest = cur.fetchone()
        ret.append(rest)
    cur.close()
    return ret