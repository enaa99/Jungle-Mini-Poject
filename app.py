from flask import Flask, render_template, jsonify,request
from bson import ObjectId
from pymongo import MongoClient
app = Flask(__name__)
from dotenv import dotenv_values
# from flask_bcrypt import Bcrypt
import bcrypt
import re 
# from flask_jwt_extended import JWTManager
# from flask_jwt_extended import create_access_token

# HOST = "3.35.139.196"
# USERNAME = "test"
# PASSWORD = "test"


# config = dotenv_values(".env")
# Bcrypt = bcrypt(app)
app.config["JWT_SECRET_KEY"] = "team-six"
# jwt = JWTManager(app)

client = MongoClient("3.35.139.196",
                  username="test",
                 password="test")

# config = dotenv_values(".env")
# client = MongoClient(config['HOST'],
#                   username=config['USERNAME'],
#                  password=config['PASSWORD'])
db = client.dbjungle
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/memo', methods=['GET'])
def get_memos():
    result = list(db.memos.find({}).sort('like', -1))

    # type ObjectId를 type String으로 변환합니다.
    for i in range(len(result)):
        objectId = result[i]['_id']
        result[i]['_id'] = str(objectId)
    return jsonify({'result': 'success', 'memos': result})
    
@app.route('/memo', methods=['POST'])
def post_memos():
    title_receive = request.form['title_give']  
    content_receive = request.form['content_give']

    memo = {'title': title_receive, 'content': content_receive, 'like' : 0}

    db.memos.insert_one(memo)

    return jsonify({'result': 'success'})

@app.route('/memo', methods=['PUT'])
def put_memo():
    id_receive = request.form['id_give']
    title_receive = request.form['title_give']  
    content_receive = request.form['content_give'] 
    
    # type String을 type ObjectId로 변환합니다.
    objectId = ObjectId(id_receive) 

    db.memos.update_one({'_id': objectId}, {'$set': {'title': title_receive, 'content': content_receive}})

    return jsonify({'result': 'success'})

@app.route('/memo', methods=['DELETE'])
def delete_memo():
    id_receive = request.form['id_give']   
    
    objectId = ObjectId(id_receive)

    db.memos.delete_one({'_id': objectId})

    return jsonify({'result': 'success'})

@app.route('/like', methods=['PUT'])
def like_memo():
    id_receive = request.form['id_give']
    
    objectId = ObjectId(id_receive)

    memo = db.memos.find_one({'_id': objectId})
    new_like = memo['like'] + 1

    db.memos.update_one({'_id': objectId}, {'$set': {'like': new_like}})

    return jsonify({'result': 'success'})

@app.route('/auth/signup', methods=['GET'])
def user_signup():
   return render_template('register.html') 

@app.route('/auth/register', methods=['POST'])
def user_register():
   #get user information
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']  
    name_receive = request.form['name_give'] 
    email_receive = request.form['email_give']
    class_receive = request.form['class_give']

   #data validation check

    if not id_receive or not password_receive or not name_receive or not email_receive or not class_receive:
      return jsonify({'result' : '하나 이상의 데이터가 입력되지 않았습니다.'})

   #id duplication check
    duplicate_check = db.user.find_one({'id':id_receive})
    print(duplicate_check)
    if duplicate_check is not None:
        return jsonify({'result' : '아이디가 중복되었습니다!'})
 
    #password string check
    if len(password_receive) < 8:
        return jsonify({'result' : '비밀번호는 8자리 이상으로 입력하세요.'}) 
    elif re.search('[0-9]+', password_receive) is None:
        return jsonify({'비밀번호에 1개 이상의 숫자를 포함해주세요.'})
    elif re.search('[a-zA-Z]+', password_receive) is None:
        return jsonify({'비밀번호에 1개 이상의 영문 대소문자를 포함해주세요.'})
    elif re.search('[`~!@#$%^&*(),<.>/?]+',password_receive) is None:
        return jsonify({'비밀번호에 1개 이상의 특수문자를 포함해주세요.'})
    
    #password hasing  
    pw_hash = bcrypt.hashpw(password_receive.encode("utf-8"), bcrypt.gensalt())

    #insert user information to database
    user = {'id' : id_receive, 'password' : pw_hash, 'name' : name_receive, 'email' : email_receive
    , 'class' : class_receive}
    db.user.insert_one(user)
    return jsonify({'result' : 'success'}) 

       


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)