import sqlite3
import pandas as pd
co = sqlite3.connect('weebcheck.db')
c = co.cursor()
resul = c.execute("SELECT * FROM animelist")
rec1= c.fetchall()
c.close()
data = []
index = 0
for i in rec1:
    g1 = ""
    g2 = ""
    g3 = ""
    g4 = ""
    g5 = ""
    if i[9] is not None:
        g1 = str.lower(i[9])
    if i[10] is not None:
        g2 = str.lower(i[10])
    if i[11] is not None:
        g3 = str.lower(i[11])
    if i[12] is not None:
        g4 = str.lower(i[12])
    if i[13] is not None:
        g5 = str.lower(i[13])
    combined = g1 + " " + g2 + " " + g3 + " " + g4 + " " +g5
    l1 = [index,i[1],combined]
    data.append(l1)
    index = index + 1
df = pd.DataFrame(data, columns = ['Index','Name', 'Combined'])
# print(df)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

cv = CountVectorizer()
count_matrix = cv.fit_transform(df["Combined"])

cosine_sim = cosine_similarity(count_matrix)
# print(cosine_sim)
