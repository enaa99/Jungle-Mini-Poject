from datetime import datetime
from distutils.debug import DEBUG
from os import access
from sqlite3 import Time
from flask import Flask, render_template, jsonify, request
from bson import ObjectId
from dotenv import dotenv_values
import jwt
import bcrypt
app = Flask(__name__)

from pymongo import MongoClient

config = dotenv_values(".env")
client = MongoClient(config['HOST'],
                  username=config['USERNAME'],
                 password=config['PASSWORD'])
db = client.dbjungle
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


SECRET_KEY = 'jungle'


@app.route('/')
def home():
   return render_template('index.html')

@app.route('/auth/signin', methods=['POST'])
def post_signin():
    name_receive = request.form['uid']
    pwd_receive = request.form['pwd']

    user_data = db.user.find_one({'id':name_receive})
    print(user_data)
    if user_data != None :
        encrypted_password = user_data['password']
        print(encrypted_password)
        print('1')
        print(bcrypt.checkpw(pwd_receive.encode("utf-8"), encrypted_password))
        print('2')

        if bcrypt.checkpw(pwd_receive.encode("utf-8"), encrypted_password) :
            payload = {
                'id':name_receive,
                #유효시간 설정하기
                'expire': False,
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({'result': 'success', 'token': token})
        else:
            return jsonify({'result':'failed'})
    else:
        return jsonify({'result':'아이디가 존재하지 않습니다'})





# @app.route('/memo', methods=['GET'])
# def get_memos():
#     result = list(db.memos.find({}).sort('like', -1))

#     # type ObjectId를 type String으로 변환합니다.
#     for i in range(len(result)):
#         objectId = result[i]['_id']
#         result[i]['_id'] = str(objectId)
#     return jsonify({'result': 'success', 'memos': result})
    

# @app.route('/memo', methods=['POST'])
# def post_memos():
#     title_receive = request.form['title_give']  
#     content_receive = request.form['content_give']

#     memo = {'title': title_receive, 'content': content_receive, 'like' : 0}

#     db.memos.insert_one(memo)

#     return jsonify({'result': 'success'})

# @app.route('/memo', methods=['PUT'])
# def put_memo():
#     id_receive = request.form['id_give']
#     title_receive = request.form['title_give']  
#     content_receive = request.form['content_give'] 
    
#     # type String을 type ObjectId로 변환합니다.
#     objectId = ObjectId(id_receive) 

#     db.memos.update_one({'_id': objectId}, {'$set': {'title': title_receive, 'content': content_receive}})

#     return jsonify({'result': 'success'})

# @app.route('/memo', methods=['DELETE'])
# def delete_memo():
#     id_receive = request.form['id_give']   
    
#     objectId = ObjectId(id_receive)

#     db.memos.delete_one({'_id': objectId})

#     return jsonify({'result': 'success'})

# @app.route('/like', methods=['PUT'])
# def like_memo():
#     id_receive = request.form['id_give']
    
#     objectId = ObjectId(id_receive)

#     memo = db.memos.find_one({'_id': objectId})
#     new_like = memo['like'] + 1

#     db.memos.update_one({'_id': objectId}, {'$set': {'like': new_like}})

#     return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)