from flask_api import FlaskAPI
from flask_pymongo import PyMongo

class Config:
    MONGO_URI="mongodb://localhost:27017/dailystar"
    DEBUG=True
    

mongo = PyMongo()
app = FlaskAPI(__name__)
app.config.from_object(Config)

mongo.init_app(app)

@app.route('/', methods=['GET'])
def root():
    return {
        'hello' : mongo.db.news.find_one({}, {"_id" : 0})
    }




if __name__ == '__main__':
    app.run(debug=True)