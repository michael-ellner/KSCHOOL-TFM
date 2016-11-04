from flask import Flask, render_template
from flask.ext.cors import CORS, cross_origin


app=Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/foo")
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def wc_cloud():
	return render_template("tweet.html")




if __name__== '__main__':
    app.run(port=4000 ,debug=True)

