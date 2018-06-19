from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
import sqlite3, time
import operator
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps


gusername = ""
gid = ""

app = Flask(__name__)
co = sqlite3.connect('weebcheck.db')
c = co.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT , name VARCHAR(100), email VARCHAR(100), username VARCHAR(50), password VARCHAR(100), register TIMESTAMP DEFAULT CURRENT_TIMESTAMP, noofusers INTEGER, favourite INTEGER)")
c.close()
class ReusableForm(Form):
    search = StringField('Search', [validators.Length(min=1,max=30)])

@app.route('/', methods=['GET','POST'])
def main():
    return render_template('index.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


@app.route('/signup', methods=['GET','POST'])
def signup():

    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = str(form.name.data)
        email = str(form.email.data)
        username = str(form.username.data)
        password = str(sha256_crypt.encrypt(str(form.password.data)))
        conn = sqlite3.connect('weebcheck.db')
        cur = conn.cursor()
        results = cur.execute("SELECT * FROM users WHERE username = ?", [username])
        result = cur.fetchone()
        if result is not None:
            cur.close()
            flash('Username already exists', 'warning')
            return redirect(url_for('signup'))
        cems = cur.execute("SELECT * FROM users WHERE email = ?", [email])
        cem = cur.fetchone()
        if cem is not None:
            cur.close()
            flash('Email already in use', 'warning')
            return redirect(url_for('signup'))

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(?, ?, ?, ?)", (name, email, username, password))
        conn.commit()
        cur.close()
        cu = conn.cursor()
        cu.execute("INSERT INTO genres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,1,1,1,1,1,1,1,1)", (username,))
        cu.execute("INSERT INTO mgenres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,1,1,1,1,1,1,1,1)", (username,))
        conn.commit()
        cu.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('main'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        conn = sqlite3.connect('weebcheck.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = ?", [username])
        data = cur.fetchone()
        if data is not None:            
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                global gusername
                gusername = username
                # print(gusername)
                flash('You are now logged in', 'success')
                cur.close()
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Login','danger')
                cur.close()
                return redirect('login')
        else:
            flash('Username not found','danger')
            cur.close()
            return redirect('login')
    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'warning')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('main'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    global gusername
    # print("username= "+gusername)
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM userfavourite WHERE username = ?", [gusername])
    data = cur.fetchall()
    cur.close()
    curs = conn.cursor()
    list1=[]
    for ids in data:
        res = curs.execute("SELECT * FROM animelist WHERE id = ?", [ids['animeid']])
        rest = curs.fetchone()
        #intol = dict(zip([c[0] for c in curs.description], rest))
        list1.append(rest)
        #print(intol['name'])
    curs.close()
    curso = conn.cursor()
    result = curso.execute("SELECT * FROM muserfavourite WHERE username = ?", [gusername])
    data = curso.fetchall()
    list2=[]
    for ids in data:
        res = curso.execute("SELECT * FROM mangalist WHERE id = ?", [ids['mangaid']])
        rest = curso.fetchone()
        #intol = dict(zip([c[0] for c in curs.description], rest))
        list2.append(rest)
        #print(intol['name'])
    curso.close()
    cu = conn.cursor()
    resul = cu.execute("SELECT * FROM genres WHERE username = ?", [gusername])
    sc = cu.fetchone()
    sco = dict(zip([c[0] for c in cu.description], sc))
    scores = []
    genrelis = []
    for key in sco.keys():
        if key == 'username':
            continue
        else:
            genrelis.append(key)
            scores.append(sco[key])
    scores, genrelis = zip(*sorted(zip(scores, genrelis)))
    # print(genrelis)
    # print(scores)
    resul = cu.execute("SELECT * FROM animelist WHERE genre1 = ?", (genrelis[7],))
    rec1=cu.fetchall()
    resul = cu.execute("SELECT * FROM animelist WHERE genre1 = ?", (genrelis[6],))
    rec2 = cu.fetchall()
    resul = cu.execute("SELECT * FROM animelist WHERE genre2 = ?", (genrelis[7],))
    rec3=cu.fetchall()
    resul = cu.execute("SELECT * FROM animelist WHERE genre2 = ?", (genrelis[6],))
    rec4=cu.fetchall()
    resul = cu.execute("SELECT * FROM animelist WHERE genre1 = ?", (genrelis[5],))
    rec5=cu.fetchall()
    resul = cu.execute("SELECT * FROM animelist WHERE genre3 = ?", (genrelis[7],))
    rec6=cu.fetchall()
    resul = cu.execute("SELECT * FROM animelist WHERE genre3 = ?", (genrelis[6],))
    rec7=cu.fetchall()
    mresul = cu.execute("SELECT * FROM mgenres WHERE username = ?", [gusername])
    msc = cu.fetchone()
    msco = dict(zip([c[0] for c in cu.description], msc))
    mscores = []
    mgenrelis = []
    for key in msco.keys():
        if key == 'username':
            continue
        else:
            mgenrelis.append(key)
            mscores.append(msco[key])
    mscores, mgenrelis = zip(*sorted(zip(mscores, mgenrelis)))
    # print(mgenrelis)
    # print(mscores)
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre1 = ?", (mgenrelis[7],))
    mrec1=cu.fetchall()
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre1 = ?", (mgenrelis[6],))
    mrec2 = cu.fetchall()
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre2 = ?", (mgenrelis[7],))
    mrec3=cu.fetchall()
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre2 = ?", (mgenrelis[6],))
    mrec4=cu.fetchall()
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre1 = ?", (mgenrelis[5],))
    mrec5=cu.fetchall()
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre3 = ?", (mgenrelis[7],))
    mrec6=cu.fetchall()
    mresul = cu.execute("SELECT * FROM mangalist WHERE genre3 = ?", (mgenrelis[6],))
    mrec7=cu.fetchall()



    return render_template('dashboard.html',list1=list1,list2=list2,rec1=rec1,rec2=rec2,rec3=rec3,rec4=rec4,rec5=rec5,rec6=rec6,rec7=rec7,mrec1=mrec1,mrec2=mrec2,mrec3=mrec3,mrec4=mrec4,mrec5=mrec5,mrec6=mrec6,mrec7=mrec7)


@app.route('/animelist/<string:id>/')
def anime(id):
    global gusername
    flag = 0
    f1 = 0
    f2 = 0
    f3 = 0
    f4 = 0
    conn = sqlite3.connect('weebcheck.db')
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM animelist WHERE id = ?",[id])
    ani = cur.fetchone()
    anim = dict(zip([c[0] for c in cur.description], ani))
    res = cur.execute("SELECT * FROM userfavourite WHERE username = ?  AND animeid = ?",(gusername,id))
    d1 = cur.fetchone()
    if d1 is not None:
        f1=1
    res = cur.execute("SELECT * FROM watched WHERE username = ?  AND animeid = ?",(gusername,id))
    d2 = cur.fetchone()
    if d2 is not None:
        f2=1
    res = cur.execute("SELECT * FROM watching WHERE username = ?  AND animeid = ?",(gusername,id))
    d3 = cur.fetchone()
    if d3 is not None:
        f3=1
    res = cur.execute("SELECT * FROM planing WHERE username = ?  AND animeid = ?",(gusername,id))
    d4 = cur.fetchone()
    if d4 is not None:
        f4=1
    cur.close()
    stri = ""
    for alpha in anim['name']:
        if alpha == "_":
            stri = stri + " "
        else:
            stri = stri + alpha
    anim['name'] = stri
    cu = conn.cursor()
    res = cu.execute("SELECT * FROM userrating WHERE username = ?  AND animeid = ?",(gusername,id))

    lis = []
    myrating = 11
    for i in res:
        lis.append(i)

    conn.commit()
    cu.close()
    if lis:
        flag=1
        myrating = lis[0][2]

    cur = conn.cursor()
    req = cur.execute("SELECT * FROM userrating WHERE animeid=?",(id,))
    req_lis = []
    for i in req:
        req_lis.append(i)
    no_users = 0
    summ = 0
    avg = 0
    for user_rating in req_lis:
        summ = summ + user_rating[2]
        no_users+=1
    if no_users:
        avg = round(summ/no_users,5)
    else:
        avg = 0
    return render_template('animepage.html',anim=anim,flag=flag,myrating=myrating,avg=avg,f1=f1,f2=f2,f3=f3,f4=f4)


@app.route('/mangalist/<string:id>/')
def manga(id):
    global gusername
    flag = 0
    f1 = 0
    f2 = 0
    f3 = 0
    f4 = 0
    conn = sqlite3.connect('weebcheck.db')
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM mangalist WHERE id = ?",[id])
    ani = cur.fetchone()
    mang = dict(zip([c[0] for c in cur.description], ani))
    res = cur.execute("SELECT * FROM muserfavourite WHERE username = ?  AND mangaid = ?",(gusername,id))
    d1 = cur.fetchone()
    if d1 is not None:
        f1=1
    res = cur.execute("SELECT * FROM mwatched WHERE username = ?  AND mangaid = ?",(gusername,id))
    d2 = cur.fetchone()
    if d2 is not None:
        f2=1
    res = cur.execute("SELECT * FROM mwatching WHERE username = ?  AND mangaid = ?",(gusername,id))
    d3 = cur.fetchone()
    if d3 is not None:
        f3=1
    res = cur.execute("SELECT * FROM mplaning WHERE username = ?  AND mangaid = ?",(gusername,id))
    d4 = cur.fetchone()
    if d4 is not None:
        f4=1
    cur.close()
    stri = ""
    for alpha in mang['name']:
        if alpha == "_":
            stri = stri + " "
        else:
            stri = stri + alpha
    mang['name'] = stri
    cu = conn.cursor()
    res = cu.execute("SELECT * FROM muserrating WHERE username = ?  AND mangaid = ?",(gusername,id))
    lis = []
    myrating = 11
    for i in res:
        lis.append(i)

    conn.commit()
    cu.close()
    if lis:
        flag=1
        myrating = lis[0][2]

    cur = conn.cursor()
    req = cur.execute("SELECT * FROM muserrating WHERE mangaid=?",(id,))
    req_lis = []
    for i in req:
        req_lis.append(i)
    no_users = 0
    summ = 0
    avg = 0
    for user_rating in req_lis:
        summ = summ + user_rating[2]
        no_users+=1
    if no_users:
        avg = round(summ/no_users,5)
    else:
        avg = 0
    return render_template('mangapage.html',mang=mang,flag=flag,myrating=myrating,avg=avg,f1=f1,f2=f2,f3=f3,f4=f4)


@app.route('/animelist')
def animelis():
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM animelist")
    animelis = cur.fetchall()
    cur.close()
    cur = conn.cursor()
    resu = cur.execute("SELECT * FROM userfavourite WHERE username = ?",[gusername])
    favlis = cur.fetchall()
    cur.close()
    animelist = []
    favid = []
    for item in animelis:
        animelist.append(item)
    for item in favlis:
        favid.append(item['animeid'])
    animelist.sort(key=operator.itemgetter('rating'))
    animelist.reverse()
    return render_template('animelist.html', animelist=animelist,favid=favid)


@app.route('/mangalist')
def mangalis():
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM mangalist")
    mangalis = cur.fetchall()
    cur.close()
    cur = conn.cursor()
    resu = cur.execute("SELECT * FROM muserfavourite WHERE username = ?",[gusername])
    favmlis = cur.fetchall()
    cur.close()
    mangalist = []
    favmid = []
    for item in mangalis:
        mangalist.append(item)
    for item in favmlis:
        favmid.append(item['mangaid'])
    mangalist.sort(key=operator.itemgetter('rating'))
    mangalist.reverse()
    return render_template('mangalist.html', mangalist=mangalist,favmid=favmid)


score = [0,0,0,0,0,0,0,0]


def fillscore(dictlist):
    global score
    score = [0,0,0,0,0,0,0,0]
    if dictlist['genre1'] is not None:
        if dictlist['genre1'] == "Action":
            score[0] += 10
        elif dictlist['genre1'] == "Comedy":
            score[1] += 10
        elif dictlist['genre1'] == "Thriller":
            score[2] += 10
        elif dictlist['genre1'] == "Drama":
            score[3] += 10
        elif dictlist['genre1'] == "Sci-Fi":
            score[4] += 10
        elif dictlist['genre1'] == "Romance":
            score[5] += 10
        elif dictlist['genre1'] == "Fantasy":
            score[6] += 10
        elif dictlist['genre1'] == "Mystery":
            score[7] += 10
    if dictlist['genre2'] is not None:
        if dictlist['genre2'] == "Action":
            score[0] += 9
        elif dictlist['genre2'] == "Comedy":
            score[1] += 9
        elif dictlist['genre2'] == "Thriller":
            score[2] += 9
        elif dictlist['genre2'] == "Drama":
            score[3] += 9
        elif dictlist['genre2'] == "Sci-Fi":
            score[4] += 9
        elif dictlist['genre2'] == "Romance":
            score[5] += 9
        elif dictlist['genre2'] == "Fantasy":
            score[6] += 9
        elif dictlist['genre2'] == "Mystery":
            score[7] += 9
    if dictlist['genre3'] is not None:
        if dictlist['genre3'] == "Action":
            score[0] += 8
        elif dictlist['genre3'] == "Comedy":
            score[1] += 8
        elif dictlist['genre3'] == "Thriller":
            score[2] += 8
        elif dictlist['genre3'] == "Drama":
            score[3] += 8
        elif dictlist['genre3'] == "Sci-Fi":
            score[4] += 8
        elif dictlist['genre3'] == "Romance":
            score[5] += 8
        elif dictlist['genre3'] == "Fantasy":
            score[6] += 8
        elif dictlist['genre3'] == "Mystery":
            score[7] += 8
    if dictlist['genre4'] is not None:
        if dictlist['genre4'] == "Action":
            score[0] += 7
        elif dictlist['genre4'] == "Comedy":
            score[1] += 7
        elif dictlist['genre4'] == "Thriller":
            score[2] += 7
        elif dictlist['genre4'] == "Drama":
            score[3] += 7
        elif dictlist['genre4'] == "Sci-Fi":
            score[4] += 7
        elif dictlist['genre4'] == "Romance":
            score[5] += 7
        elif dictlist['genre4'] == "Fantasy":
            score[6] += 7
        elif dictlist['genre4'] == "Mystery":
            score[7] += 7
    return 1


@app.route('/added/<string:id>/')
def added(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO userfavourite(username,animeid) VALUES(?,?)", (gusername,id))
    conn.commit()
    cur.close()
    curs = conn.cursor()
    resu = curs.execute("SELECT * FROM animelist WHERE id = ?",[id])
    animel = curs.fetchone()

    curs.close()
    
    d=fillscore(animel)
    
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM genres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    global score
    score[0]=int(genrel['Action']) + score[0]
    score[1]=int(genrel['Comedy']) + score[1]
    score[2]=int(genrel['Thriller']) + score[2]
    score[3]=int(genrel['Drama']) + score[3]
    score[4]=int(genrel['Sci']) + score[4]
    score[5]=int(genrel['Romance']) + score[5]
    score[6]=int(genrel['Fantasy']) + score[6]
    score[7]=int(genrel['Mystery']) + score[7]
    curso.execute("DELETE FROM genres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO genres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    return redirect(url_for('animelis'))


@app.route('/addedp/<string:id>/')
def addedp(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO userfavourite(username,animeid) VALUES(?,?)", (gusername,id))
    conn.commit()
    cur.close()
    curs = conn.cursor()
    resu = curs.execute("SELECT * FROM animelist WHERE id = ?",[id])
    animel = curs.fetchone()

    curs.close()
    
    d=fillscore(animel)
    
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM genres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    global score
    score[0]=int(genrel['Action']) + score[0]
    score[1]=int(genrel['Comedy']) + score[1]
    score[2]=int(genrel['Thriller']) + score[2]
    score[3]=int(genrel['Drama']) + score[3]
    score[4]=int(genrel['Sci']) + score[4]
    score[5]=int(genrel['Romance']) + score[5]
    score[6]=int(genrel['Fantasy']) + score[6]
    score[7]=int(genrel['Mystery']) + score[7]
    curso.execute("DELETE FROM genres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO genres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    return redirect('/animelist/'+str(id))


@app.route('/addedinwatched/<string:id>/')
def addedinwatched(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO watched(username,animeid) VALUES(?,?)", (gusername,id))
    res=cur.execute("SELECT * FROM watching WHERE username = ? AND animeid = ?", (gusername,id))
    if res is not None:
        cur.execute("DELETE FROM watching WHERE username = ? AND animeid = ?", (gusername,id))
    res=cur.execute("SELECT * FROM planing WHERE username = ? AND animeid = ?", (gusername,id))
    if res is not None:
        cur.execute("DELETE FROM planing WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/animelist/'+str(id))


@app.route('/addedinwatching/<string:id>/')
def addedinwatching(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO watching(username,animeid) VALUES(?,?)", (gusername,id))
    res=cur.execute("SELECT * FROM planing WHERE username = ? AND animeid = ?", (gusername,id))
    if res is not None:
        cur.execute("DELETE FROM planing WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/animelist/'+str(id))


@app.route('/addedinplaning/<string:id>/')
def addedinplaning(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO planing(username,animeid) VALUES(?,?)", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/animelist/'+str(id))


@app.route('/removed/<string:id>/')
def removed(id):
    global gusername
    global score
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM animelist WHERE id = ?",[id])
    animel = cur.fetchone()
    cur.close()
    d = fillscore(animel)
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM genres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    score[0]=int(genrel['Action']) - score[0]
    score[1]=int(genrel['Comedy']) - score[1]
    score[2]=int(genrel['Thriller']) - score[2]
    score[3]=int(genrel['Drama']) - score[3]
    score[4]=int(genrel['Sci']) - score[4]
    score[5]=int(genrel['Romance']) - score[5]
    score[6]=int(genrel['Fantasy']) - score[6]
    score[7]=int(genrel['Mystery']) - score[7]
    curso.execute("DELETE FROM genres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO genres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    curs = conn.cursor()
    curs.execute("DELETE FROM userfavourite WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    curs.close()
    return redirect(url_for('animelis'))

@app.route('/removedp/<string:id>/')
def removedp(id):
    global gusername
    global score
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM animelist WHERE id = ?",[id])
    animel = cur.fetchone()
    cur.close()
    d = fillscore(animel)
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM genres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    score[0]=int(genrel['Action']) - score[0]
    score[1]=int(genrel['Comedy']) - score[1]
    score[2]=int(genrel['Thriller']) - score[2]
    score[3]=int(genrel['Drama']) - score[3]
    score[4]=int(genrel['Sci']) - score[4]
    score[5]=int(genrel['Romance']) - score[5]
    score[6]=int(genrel['Fantasy']) - score[6]
    score[7]=int(genrel['Mystery']) - score[7]
    curso.execute("DELETE FROM genres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO genres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    curs = conn.cursor()
    curs.execute("DELETE FROM userfavourite WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    curs.close()
    return redirect('/animelist/'+str(id))


@app.route('/removedinwatched/<string:id>/')
def removedinwatched(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DELETE FROM watched WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/animelist/'+str(id))

@app.route('/removedinwatching/<string:id>/')
def removedinwatching(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DELETE FROM watching WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/animelist/'+str(id))


@app.route('/removedinplaning/<string:id>/')
def removedinplaning(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DELETE FROM planing WHERE username = ? AND animeid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/animelist/'+str(id))

@app.route('/madded/<string:id>/')
def madded(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO muserfavourite(username,mangaid) VALUES(?,?)", (gusername,id))
    conn.commit()
    cur.close()
    curs = conn.cursor()
    resu = curs.execute("SELECT * FROM mangalist WHERE id = ?",[id])
    animel = curs.fetchone()

    curs.close()
    
    d=fillscore(animel)
    
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM mgenres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    global score
    score[0]=int(genrel['Action']) + score[0]
    score[1]=int(genrel['Comedy']) + score[1]
    score[2]=int(genrel['Thriller']) + score[2]
    score[3]=int(genrel['Drama']) + score[3]
    score[4]=int(genrel['Sci']) + score[4]
    score[5]=int(genrel['Romance']) + score[5]
    score[6]=int(genrel['Fantasy']) + score[6]
    score[7]=int(genrel['Mystery']) + score[7]
    curso.execute("DELETE FROM mgenres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO mgenres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    return redirect(url_for('mangalis'))


@app.route('/maddedp/<string:id>/')
def maddedp(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO muserfavourite(username,mangaid) VALUES(?,?)", (gusername,id))
    conn.commit()
    cur.close()
    curs = conn.cursor()
    resu = curs.execute("SELECT * FROM mangalist WHERE id = ?",[id])
    animel = curs.fetchone()

    curs.close()
    
    d=fillscore(animel)
    
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM mgenres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    global score
    score[0]=int(genrel['Action']) + score[0]
    score[1]=int(genrel['Comedy']) + score[1]
    score[2]=int(genrel['Thriller']) + score[2]
    score[3]=int(genrel['Drama']) + score[3]
    score[4]=int(genrel['Sci']) + score[4]
    score[5]=int(genrel['Romance']) + score[5]
    score[6]=int(genrel['Fantasy']) + score[6]
    score[7]=int(genrel['Mystery']) + score[7]
    curso.execute("DELETE FROM mgenres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO mgenres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    return redirect('/mangalist/'+str(id))


@app.route('/maddedinwatched/<string:id>/')
def maddedinwatched(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO mwatched(username,mangaid) VALUES(?,?)", (gusername,id))
    res=cur.execute("SELECT * FROM mwatching WHERE username = ? AND mangaid = ?", (gusername,id))
    if res is not None:
        cur.execute("DELETE FROM mwatching WHERE username = ? AND mangaid = ?", (gusername,id))
    res=cur.execute("SELECT * FROM mplaning WHERE username = ? AND mangaid = ?", (gusername,id))
    if res is not None:
        cur.execute("DELETE FROM mplaning WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/mangalist/'+str(id))


@app.route('/maddedinwatching/<string:id>/')
def maddedinwatching(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO mwatching(username,mangaid) VALUES(?,?)", (gusername,id))
    res=cur.execute("SELECT * FROM mplaning WHERE username = ? AND mangaid = ?", (gusername,id))
    if res is not None:
        cur.execute("DELETE FROM mplaning WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/mangalist/'+str(id))


@app.route('/maddedinplaning/<string:id>/')
def maddedinplaning(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("INSERT INTO mplaning(username,mangaid) VALUES(?,?)", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/mangalist/'+str(id))

@app.route('/mremoved/<string:id>/')
def mremoved(id):
    global gusername
    global score
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM mangalist WHERE id = ?",[id])
    animel = cur.fetchone()
    cur.close()
    d = fillscore(animel)
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM mgenres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    score[0]=int(genrel['Action']) - score[0]
    score[1]=int(genrel['Comedy']) - score[1]
    score[2]=int(genrel['Thriller']) - score[2]
    score[3]=int(genrel['Drama']) - score[3]
    score[4]=int(genrel['Sci']) - score[4]
    score[5]=int(genrel['Romance']) - score[5]
    score[6]=int(genrel['Fantasy']) - score[6]
    score[7]=int(genrel['Mystery']) - score[7]
    curso.execute("DELETE FROM mgenres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO mgenres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    curs = conn.cursor()
    curs.execute("DELETE FROM muserfavourite WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    curs.close()
    return redirect(url_for('mangalis'))

@app.route('/mremovedp/<string:id>/')
def mremovedp(id):
    global gusername
    global score
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM mangalist WHERE id = ?",[id])
    animel = cur.fetchone()
    cur.close()
    d = fillscore(animel)
    curso = conn.cursor()
    resul = curso.execute("SELECT * FROM mgenres WHERE username = ?",(gusername,))
    genrel = curso.fetchone()
    score[0]=int(genrel['Action']) - score[0]
    score[1]=int(genrel['Comedy']) - score[1]
    score[2]=int(genrel['Thriller']) - score[2]
    score[3]=int(genrel['Drama']) - score[3]
    score[4]=int(genrel['Sci']) - score[4]
    score[5]=int(genrel['Romance']) - score[5]
    score[6]=int(genrel['Fantasy']) - score[6]
    score[7]=int(genrel['Mystery']) - score[7]
    curso.execute("DELETE FROM mgenres WHERE username = ?", (gusername,))
    curso.execute("INSERT INTO mgenres(username,Action,Comedy,Thriller,Drama,Sci,Romance,Fantasy,Mystery) VALUES(?,?,?,?,?,?,?,?,?)",(gusername,score[0],score[1],score[2],score[3],score[4],score[5],score[6],score[7]))
    conn.commit()
    curso.close()
    curs = conn.cursor()
    curs.execute("DELETE FROM muserfavourite WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    curs.close()
    return redirect('/mangalist/'+str(id))


@app.route('/mremovedinwatched/<string:id>/')
def mremovedinwatched(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DELETE FROM mwatched WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/mangalist/'+str(id))


@app.route('/mremovedinwatching/<string:id>/')
def mremovedinwatching(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DELETE FROM mwatching WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/mangalist/'+str(id))


@app.route('/mremovedinplaning/<string:id>/')
def mremovedinplaning(id):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("DELETE FROM mplaning WHERE username = ? AND mangaid = ?", (gusername,id))
    conn.commit()
    cur.close()

    return redirect('/mangalist/'+str(id))

@app.route('/animelist/<string:id>/<int:stars>/<string:a>/')
def star(id,stars,a):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if a=="1":
        cur.execute("INSERT INTO userrating(username,animeid,rating) VALUES(?,?,?)", (gusername,id,stars))
        resu = cur.execute("SELECT * FROM animelist WHERE id=?",[id])
        lisu = []
        for i in resu:
            lisu.append(i)
        avgrating = round((int(lisu[0][17])*float(lisu[0][5]) + stars)/((int(lisu[0][17])+1)*1.0),5)
        
        cur.execute("DELETE FROM animelist WHERE id = ?", [id])
        conn.commit()
        cur.execute("INSERT INTO animelist (id, name, description, imagelink, shortimage, rating, episodes, producer, licensor, genre1,  genre2, genre3, genre4, genre5, genre6, genre7, genre8, noofusers, favourite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)" , (id, lisu[0][1], lisu[0][2], lisu[0][3], lisu[0][4], avgrating,lisu[0][6], lisu[0][7], lisu[0][8], lisu[0][9],  lisu[0][10], lisu[0][11], lisu[0][12], lisu[0][13], lisu[0][14], lisu[0][15], lisu[0][16],int(lisu[0][17])+1,0))
    else:
        resul = cur.execute("SELECT * FROM userrating WHERE username = ? AND animeid =?",(gusername,id))
        lisul = []
        for i in resul:
            lisul.append(i)
        cur.execute("DELETE FROM userrating WHERE username = ? AND animeid = ?", (gusername,id))
        cur.execute("INSERT INTO userrating(username,animeid,rating) VALUES(?,?,?)", (gusername,id,stars))
        resu = cur.execute("SELECT * FROM animelist WHERE id=?",[id])
        lisu = []
        for i in resu:
            lisu.append(i)
        oldrating = int(lisul[0][2])

        avgrating = round(float(lisu[0][5])+(stars - oldrating)/(int(lisu[0][17])*1.0),5)
        cur.execute("DELETE FROM animelist WHERE id = ?", [id])
        conn.commit()
        cur.execute("INSERT INTO animelist (id, name, description, imagelink, shortimage, rating, episodes, producer, licensor, genre1,  genre2, genre3, genre4, genre5, genre6, genre7, genre8, noofusers, favourite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)" , (id, lisu[0][1], lisu[0][2], lisu[0][3], lisu[0][4], avgrating,lisu[0][6], lisu[0][7], lisu[0][8], lisu[0][9],  lisu[0][10], lisu[0][11], lisu[0][12], lisu[0][13], lisu[0][14], lisu[0][15], lisu[0][16],lisu[0][17],0))
    conn.commit()
    cur.close()
    return redirect('/animelist/'+str(id))


@app.route('/mangalist/<string:id>/<int:stars>/<string:a>/')
def mstar(id,stars,a):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if a=="1":
        cur.execute("INSERT INTO muserrating(username,mangaid,rating) VALUES(?,?,?)", (gusername,id,stars))
        resu = cur.execute("SELECT * FROM mangalist WHERE id=?",[id])
        lisu = []
        for i in resu:
            lisu.append(i)

        avgrating = round((int(lisu[0][16])*float(lisu[0][5]) + stars)/((int(lisu[0][16])+1)*1.0),5)

        cur.execute("DELETE FROM mangalist WHERE id = ?", [id])
        conn.commit()
        cur.execute("INSERT INTO mangalist (id, name, description, imagelink, shortimage, rating, volumes, author, genre1,  genre2, genre3, genre4, genre5, genre6, genre7, genre8, noofusers, favourite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" , (id, lisu[0][1], lisu[0][2], lisu[0][3], lisu[0][4], avgrating,lisu[0][6], lisu[0][7], lisu[0][8], lisu[0][9],  lisu[0][10], lisu[0][11], lisu[0][12], lisu[0][13], lisu[0][14], lisu[0][15], int(lisu[0][16])+1,0))

    else:
        resul = cur.execute("SELECT * FROM muserrating WHERE username = ? AND mangaid =?",(gusername,id))
        lisul = []
        for i in resul:
            lisul.append(i)
        cur.execute("DELETE FROM muserrating WHERE username = ? AND mangaid = ?", (gusername,id))
        cur.execute("INSERT INTO muserrating(username,mangaid,rating) VALUES(?,?,?)", (gusername,id,stars))
        resu = cur.execute("SELECT * FROM mangalist WHERE id=?",[id])
        lisu = []
        for i in resu:
            lisu.append(i)
        oldrating = int(lisul[0][2])

        avgrating = round(float(lisu[0][5])+(stars - oldrating)/(int(lisu[0][16])*1.0),5)

        cur.execute("DELETE FROM mangalist WHERE id = ?", [id])
        conn.commit()
        cur.execute("INSERT INTO mangalist (id, name, description, imagelink, shortimage, rating, volumes, author, genre1,  genre2, genre3, genre4, genre5, genre6, genre7, genre8, noofusers, favourite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" , (id, lisu[0][1], lisu[0][2], lisu[0][3], lisu[0][4], avgrating,lisu[0][6], lisu[0][7], lisu[0][8], lisu[0][9],  lisu[0][10], lisu[0][11], lisu[0][12], lisu[0][13], lisu[0][14], lisu[0][15], lisu[0][16],0))
    conn.commit()
    cur.close()
    return redirect('/mangalist/'+str(id))


@app.route('/otherusers')
def ou():
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    allusers = []
    for lists in data:
        f2 = 0
        f3 = 0
        f4 = 0
        f5 = 0
        f6 = 0
        f7 = 0
        res = cur.execute("SELECT * FROM watched WHERE username = ?",(lists[3],))
        d2 = cur.fetchone()
        if d2 is not None:
            f2=1
        res = cur.execute("SELECT * FROM watching WHERE username = ?",(lists[3],))
        d3 = cur.fetchone()
        if d3 is not None:
            f3=1
        res = cur.execute("SELECT * FROM planing WHERE username = ?",(lists[3],))
        d4 = cur.fetchone()

        if d4 is not None:
            f4=1
        mres = cur.execute("SELECT * FROM mwatched WHERE username = ?",(lists[3],))
        d5 = cur.fetchone()
        if d5 is not None:
            f5=1
        mres = cur.execute("SELECT * FROM mwatching WHERE username = ?",(lists[3],))
        d6 = cur.fetchone()
        if d6 is not None:
            f6=1
        mres = cur.execute("SELECT * FROM mplaning WHERE username = ?",(lists[3],))
        d7 = cur.fetchone()
        if d7 is not None:
            f7=1
        if lists[3] != gusername:
            if f2==1 or f3==1 or f4==1 or f5==1 or f6==1 or f7==1:
                allusers.append(lists[3])
    cur.close()
    return render_template('otherusers.html',allusers=allusers)


@app.route('/otherusers/<string:uname>')
def ous(uname):
    fl1=0
    fl2=0
    fl3=0
    fl4=0
    fl5=0
    fl6=0
    conn = sqlite3.connect('weebcheck.db')
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM watched WHERE username = ?",(uname,))
    wed = cur.fetchall()
    res = cur.execute("SELECT * FROM watching WHERE username = ?",(uname,))
    wing = cur.fetchall()
    res = cur.execute("SELECT * FROM planing WHERE username = ?",(uname,))
    ping = cur.fetchall()
    res = cur.execute("SELECT * FROM mwatched WHERE username = ?",(uname,))
    mwed = cur.fetchall()
    mres = cur.execute("SELECT * FROM mwatching WHERE username = ?",(uname,))
    mwing = cur.fetchall()
    mres = cur.execute("SELECT * FROM mplaning WHERE username = ?",(uname,))
    mping = cur.fetchall()
    watching=[]
    watched=[]
    planing=[]
    mwatching=[]
    mwatched=[]
    mplaning=[]

    for items in wed:
        res = cur.execute("SELECT * FROM animelist WHERE id=?",(items[1],))
        ls1 = cur.fetchone()
        watched.append(ls1)
        if ls1 is not None:
            fl1=1
    for items in wing:
        res = cur.execute("SELECT * FROM animelist WHERE id=?",(items[1],))
        ls2 = cur.fetchone()
        watching.append(ls2)
        if ls2 is not None:
            fl2=1
    for items in ping:
        res = cur.execute("SELECT * FROM animelist WHERE id=?",(items[1],))
        ls3 = cur.fetchone()
        planing.append(ls3)
        if ls3 is not None:
            fl3=1
    for items in mwed:
        res = cur.execute("SELECT * FROM mangalist WHERE id=?",(items[1],))
        ls1 = cur.fetchone()
        mwatched.append(ls1)
        if ls1 is not None:
            fl4=1
    for items in mwing:
        res = cur.execute("SELECT * FROM mangalist WHERE id=?",(items[1],))
        ls2 = cur.fetchone()
        mwatching.append(ls2)
        if ls2 is not None:
            fl5=1
    for items in mping:
        res = cur.execute("SELECT * FROM mangalist WHERE id=?",(items[1],))
        ls3 = cur.fetchone()
        mplaning.append(ls3)
        if ls3 is not None:
            fl6=1
    cur.close()
    return render_template('oupage.html',watched=watched,watching=watching,planing=planing,mwatched=mwatched,mwatching=mwatching,mplaning=mplaning,fl1=fl1,fl2=fl2,fl3=fl3,fl4=fl4,fl5=fl5,fl6=fl6)


@app.route('/blogs')
def blogs():
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    cur=conn.cursor()
    result=cur.execute("SELECT * FROM blogs")
    blogs=cur.fetchall()
    result2=cur.execute("SELECT * FROM liked WHERE username=?",(gusername,))
    list_likes=cur.fetchall()
    like_ids=[]
    cur.close()
    for items in list_likes:
        like_ids.append(items[1])
    if result is not None:
        return render_template('articles.html',blogs=blogs,like_ids=like_ids)
    else:
        msg='No blogs Found'
        return render_template('articles.html',msg=msg)


@app.route('/blogs/<string:id>/')
def blog(id):
    conn = sqlite3.connect('weebcheck.db')
    cur=conn.cursor()
    result=cur.execute("SELECT * FROM blogs WHERE id=?",[id])
    blog=cur.fetchone()
    result2=cur.execute("SELECT * FROM comments WHERE bid=?",[id])
    comment_list=cur.fetchall()
    cur.close()
    return render_template('article.html',blog=blog,comment_list=comment_list)


class BlogForm(Form):
    title=StringField('Title',[validators.Length(min=1,max=200)])
    body=TextAreaField('Body',[validators.Length(min=1)])


@app.route('/add_blog',methods=['GET','POST'])
@is_logged_in
def add_blog():
    global gusername
    form=BlogForm(request.form)
    if request.method =='POST' and form.validate():
        title=form.title.data
        body=form.body.data
        conn = sqlite3.connect('weebcheck.db')
        cur=conn.cursor()
        cur.execute("INSERT INTO blogs(title,body,author) VALUES(?,?,?)",(title,body,gusername))
        conn.commit()
        cur.close()

        flash('Blog created','success')

        return redirect(url_for('blogs'))

    return render_template('add_article.html',form=form)


@app.route('/edit_blog/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_blog(id):
    global gusername
    #crate cursor
    conn = sqlite3.connect('weebcheck.db')
    cur=conn.cursor()
    #get article by id
    result=cur.execute("SELECT * FROM blogs WHERE id=? AND author=?",(id,gusername))
    blog=cur.fetchone()
    cur.close()

    #get form
    form=BlogForm(request.form)
    
    #populate article form fields
    form.title.data=blog[1]
    form.body.data=blog[2]

    if request.method =='POST' and form.validate():
        title=request.form['title']
        body=request.form['body']

        #create cursor
        conn = sqlite3.connect('weebcheck.db')
        curs=conn.cursor()

        #execute
        curs.execute("UPDATE blogs SET title=?, body=? WHERE id=?",(title,body,id))

        conn.commit()
        curs.close()

        flash('Blog Updated','success')

        return redirect(url_for('blogs'))

    return render_template('edit_article.html',form=form)


@app.route('/delete_blog/<string:id>')
@is_logged_in
def delete_blog(id):
    #create cursor
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    cur=conn.cursor()
    cur.execute("DELETE FROM blogs WHERE id=? AND author=?",(id,gusername))
    conn.commit()
    cur.close()

    flash('Blog Deleted','success')

    return redirect(url_for('blogs'))


@app.route('/like/<string:hid>')
def like(hid):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    cur=conn.cursor()
    cur.execute("INSERT INTO liked(username,bid) VALUES(?,?)",(gusername,hid))
    result2=cur.execute("SELECT likes FROM blogs WHERE id=?",[hid])
    temp=cur.fetchone()
    if temp[0] is not None:
        temp2=int(temp[0])+1
    else:
        temp2=1
    cur.execute("UPDATE blogs SET likes=? WHERE id=?",(temp2,hid))
    conn.commit()
    cur.close()
    return redirect('/blogs')

@app.route('/remove_like/<string:hid>')
def remove_like(hid):
    global gusername
    conn = sqlite3.connect('weebcheck.db')
    cur=conn.cursor()
    cur.execute("DELETE FROM liked WHERE bid=? AND username=?",(hid,gusername))
    result2=cur.execute("SELECT likes FROM blogs WHERE id=?",[hid])
    temp=cur.fetchone() 
    if temp[0] is not None:
        temp2=int(temp[0])-1
    else:
        temp2=0
    cur.execute("UPDATE blogs SET likes=? WHERE id=?",(temp2,hid))
    conn.commit()
    cur.close()
    return redirect('/blogs')


class ArticleForm4(Form):
    body=TextAreaField('Body',[validators.Length(min=1)])

@app.route('/viewer_reply/<string:id>',methods=['GET','POST'])
def viewer_reply(id):
    form=ArticleForm4(request.form)
    if request.method =='POST' and form.validate():
        body=form.body.data
        global gusername
        conn = sqlite3.connect('weebcheck.db')
        cur=conn.cursor()
        result=cur.execute("SELECT * FROM blogs WHERE id=?",[id])
        temp=cur.fetchone()
        cur.execute("INSERT INTO comments(comment,username,bid) VALUES(?,?,?)",(body,gusername,id))
        conn.commit()
        cur.close()
        return redirect('/blogs/'+str(id))

    return render_template('viewer_reply.html',form=form)

if __name__ == "__main__":
    app.secret_key='secret123'
    app.run(debug=True)
