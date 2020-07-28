import pandas as pd
from new_recommeder import df,cosine_sim
import sqlite3
import numpy as np

def return_similar_to_favourite(list1):
    similar_animes = np.array([0*x for x in range(len(cosine_sim[0]))])
    similar_animes = similar_animes.astype('float64') 
    for anime in list1:
        print(anime[1])
        anime_ind = df[df.Name == anime[1]]["Index"].values[0]
        similarities = cosine_sim[anime_ind]
        for e in range(len(similarities)):
            similar_animes[e] = similar_animes[e]+similarities[e]

    similar_animes = list(enumerate(similar_animes))
    sorted_similar_animes = sorted(similar_animes,key=lambda x:x[1],reverse=True)[:10]
    # print(sorted_similar_animes)
    ret = []
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for anime in sorted_similar_animes:
        res = cur.execute("SELECT * FROM animelist WHERE name = ?", [df[df.Index == anime[0]]["Name"].values[0]])
        rest = cur.fetchone()
        ret.append(rest)
    cur.close()
    return ret