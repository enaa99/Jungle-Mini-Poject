from datetime import datetime
from distutils.debug import DEBUG
from os import access
from sqlite3 import Time
from flask import Flask, render_template, jsonify, request
from bson import ObjectId
from dotenv import dotenv_values
from pymongo import MongoClient
import jwt
import bcrypt
app = Flask(__name__)

import bcrypt
import re 
# from flask_jwt_extended import JWTManager
# from flask_jwt_extended import create_access_token


config = dotenv_values(".env")

app.config["JWT_SECRET_KEY"] = "team-six"


config = dotenv_values(".env")
client = MongoClient(config['HOST'],
                  username=config['USERNAME'],
                 password=config['PASSWORD'])

db = client.dbjungle
headers = {'User-Agent' : 'Moz                                                                                                                illa/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


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



@app.route('/auth/signup', methods=['GET'])
def user_signup():
   return render_template('register.html') 

@app.route('/auth/register', methods=['POST'])
def user_register():
   #get user information
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']  
    confirm_password_receive = request.form['confirm_password_give']  
    name_receive = request.form['name_give'] 
    email_receive = request.form['email_give']
    class_receive = request.form['radio_give']
    print(id_receive, password_receive, confirm_password_receive, name_receive, email_receive, class_receive)

   #data validation check    
    if not id_receive or not password_receive or not name_receive or not email_receive or not class_receive:
      return jsonify({'result' : '하나 이상의 데이터가 입력되지 않았습니다.'})

   #id duplication check
    duplicate_check = db.user.find_one({'id':id_receive})
    print(duplicate_check)
    if duplicate_check is not None:
        return jsonify({'result' : '아이디가 중복되었습니다!'})
 
     #confirm password
    if password_receive != confirm_password_receive:
         return jsonify({'result' :'비밀번호가 동일하지 않습니다.'})
         
    #password string check
    if len(password_receive) < 8:
        return jsonify({'result' : '비밀번호는 8자리 이상으로 입력하세요.'}) 
    elif re.search('[0-9]+', password_receive) is None:
        return jsonify({'result' : '비밀번호에 1개 이상의 숫자를 포함해주세요.'})
    elif re.search('[a-zA-Z]+', password_receive) is None:
        return jsonify({'result' : '비밀번호에 1개 이상의 영문 대소문자를 포함해주세요.'})
    elif re.search('[`~!@#$%^&*(),<.>/?]+',password_receive) is None:
        return jsonify({'result' : '비밀번호에 1개 이상의 특수문자를 포함해주세요.'})


    #password hasing  
    pw_hash = bcrypt.hashpw(password_receive.encode("utf-8"), bcrypt.gensalt())

    #insert user information to database
    user = {'id' : id_receive, 'password' : pw_hash, 'name' : name_receive, 'email' : email_receive
    , 'class' : class_receive}
    db.user.insert_one(user)
    return jsonify({'result' : 'success'}) 

       


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)