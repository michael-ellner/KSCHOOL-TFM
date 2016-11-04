from flask import Flask
from flask.ext.pymongo import PyMongo

app= Flask(__name__)

app.config['MONGO_DBNAME']='KSCHOOL_TFM'
app.config['MONGO_URI']='mongodb://localhost:27017/KSCHOOL_TFM'

mongo=PyMongo(app)

@app.route('/add')
def add():
    user=mongo.db.user_ff
    user.insert({'name': 'Juan'})
    return 'Added Juan'
if __name__== '__main__':
    app.run(port=4000 ,debug=True)