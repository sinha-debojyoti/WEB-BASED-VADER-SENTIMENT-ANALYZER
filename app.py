from flask import Flask, render_template, request, jsonify, session
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import mysql.connector

app = Flask(__name__)
app.secret_key = 'debo'

'''
	MySQL Command to create user_score table
	
	CREATE TABLE user_score(
		name varchar(50),
		score varchar(50)
	);
'''

mydb = mysql.connector.connect(
        host="" 		#Enter your host name 
        user="", 		#Enter your user name 
        password="", 	#Enter your password name 
        database="" 	#Enter your database name 
    )

@app.route('/')
def index():
    if 'username' in session:
        mycursor = mydb.cursor()

        sql = "SELECT name, sum(score) FROM user_score WHERE name = %s"
        val = (session['username'],)

        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        score = (myresult[0][1])

        if score == "None":
            score = 0

        return render_template('score.html', username=session['username'], score=score)
    else:
        return render_template('index.html')

@app.route('/addscore')
def addScore():

    calscore = session['compound']
    if (calscore >= 0.5):
        calscore = 1
    elif (calscore <= -0.5):
        calscore = -1
    else:
        calscore = 0

    # Add score to database
    mycursor = mydb.cursor()
    username = session['username']
    score = calscore
    sql = "INSERT INTO user_score (name, score) VALUES (%s, %s)"
    val = (username, score)
    mycursor.execute(sql, val)
    mydb.commit()

    #Fetch Score Data from database
    mycursor = mydb.cursor()
    sql = "SELECT name, sum(score) FROM user_score WHERE name = %s"
    val = (session['username'],)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    score = (myresult[0][1])

    return render_template('score.html', username=session['username'], score=score)

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form.get('username')
    session['compound'] = 0

    mycursor = mydb.cursor()

    sql = "SELECT name, sum(score) FROM user_score WHERE name = %s"
    val = (session['username'],)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    score = (myresult[0][1])

    return render_template('score.html', username = session['username'], score = score)

@app.route('/get')
def get():
    if 'username' in session:
        return str(session['compound'])
    else:
        return 'Not log in'

@app.route('/logout')
def logout():
    # Delete session data
    session.pop('username', None)
    session.pop('compound', None)

    return render_template('index.html')

@app.route("/check", methods=['POST', 'GET'])
def check():
    messages = request.values.get("message")
    sid = SentimentIntensityAnalyzer()
    score = sid.polarity_scores(messages)
    session['compound'] = score['compound']
    return jsonify(score)


if __name__ == '__main__':
    app.debug = True
    app.run(host = "0.0.0.0")
    # app.run()
    app.run(debug=True)
