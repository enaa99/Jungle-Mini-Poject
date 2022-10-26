
from datetime import timedelta,datetime


from distutils.debug import DEBUG
from os import access
from sqlite3 import Time
from flask import Flask, render_template, jsonify, request, redirect
from bson import ObjectId, is_valid
from dotenv import dotenv_values
from pymongo import MongoClient
import jwt
import bcrypt
from pymongo import MongoClient
app = Flask(__name__)
from pymongo import MongoClient
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
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


SECRET_KEY = 'jungle'


def validate_token(token):
    try:
        user_data = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return False
    except jwt.exceptions.DecodeError:
        return False
    else:
        return user_data['id']
        

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    
    if(token_receive != None):
        is_valid = validate_token(token_receive)
        if is_valid:
            #home
            return redirect('/home')
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/auth/signin', methods=['POST'])
def post_signin():
    name_receive = request.form['uid']
    pwd_receive = request.form['pwd']
    user_data = db.user.find_one({'id':name_receive})
    print(user_data)
    if user_data != None :
        encrypted_password = user_data['password']
      

        if bcrypt.checkpw(pwd_receive.encode("utf-8"), encrypted_password) :
            payload = {
                'id':name_receive,                
                'exp': datetime.utcnow() + timedelta(hours=1),
            }
            print(datetime.utcnow())
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({'result': 'success', 'token': token.decode('utf-8')})
        else:
            return jsonify({'result':'failed'})
    else:
        return jsonify({'result':'아이디가 존재하지 않습니다'})
#home
@app.route('/home')
def homecoming():
    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)
    partys, host_party, participant_party = [], [], []
    if uid == False :
        return redirect('/')
    
    result = list(db.party.find({}))
    for r in result:
        if uid == r['host']:
            host_party.append(r)
        elif uid in r['participant']:
            participant_party.append(r)
        elif r['state'] == '0':
            partys.append(r)

    print('11111')
    print(partys)
    return render_template('home.html', partys = partys, host_party = host_party, participant_party = participant_party)
        # return render_template('home.html') 
   


@app.route('/auth/signup', methods=['GET'])
def user_signup():
   return render_template('register.html') 

@app.route('/auth/signup', methods=['POST'])
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

# 모임 리스트 조회
# @app.route('/party', methods=['GET'])
# def party_create():
    # partys = list(db.party.find({}))
    # print(partys)
    # return render_template('home.html', partys = partys)

# 모임 생성
@app.route('/party', methods=['POST'])
def party_register():
    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)
    if uid == False:
        return jsonify({'result' : 'failed'}) 
    
   #get user information
    host_receive = uid
    title_receive = request.form['title_give']  
    store_receive = request.form['store_give']  
    category_receive = request.form['category_give'] 
    menu_receive = request.form['menu_give']
    time_receive = request.form['time_give'] 
    place_receive = request.form['place_give']
    people_receive = request.form['people_give']  
    participant = [host_receive]
    print(host_receive, title_receive, store_receive, category_receive, menu_receive, place_receive, people_receive, participant)

    party_data = {'host': host_receive, 'title': title_receive, 'store': store_receive, 'category': category_receive,
                  'menu': menu_receive, 'time':time_receive, 'place': place_receive, 'people': people_receive, 'state': '0', 'participant': participant}
    db.party.insert_one(party_data)
    return jsonify({'result' : 'success'}) 

# 모임 삭제(호스트)
@app.route('/party', methods=['DELETE'])
def party_delete():
    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)
    
    if uid == False:
        return jsonify({'result':'failed'})
    
    object_id_receive = request.form['object_id_give']
    object_id = ObjectId(object_id_receive)
    party_info = db.party.find_one({'_id':object_id})
    print(party_info)
    if party_info is not None:
        if party_info['host'] == uid :
            db.party.delete_one({'_id' : object_id})
            return jsonify({'result':'success'})
        else:
            return jsonify({'result':'failed'})
    else:
        return jsonify({'result':'failed'})

# 모임 확정(호스트)
@app.route('/party',methods=['PATCH'])
def party_confirm():
    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)

    if uid == False:
        return jsonify({'result':'failed'})

    object_id_receive = request.form['object_id_give']
    object_id = ObjectId(object_id_receive)
    party_info = db.party.find_one({'_id':object_id})
    if party_info is not None :
        if (party_info['_id'] == object_id) and (uid == party_info['host']):
            db.party.update_one({'_id':object_id},{'$set':{'state':'1'}})
            print('성공')
            return jsonify({'result':'success'})       
        else:   
            print('실패1')
            return jsonify({'result':'잘못된 접근 입니다.'})
    else:
        print('실패2')
        return jsonify({'result':'모임이 존재하지 않습니다'})


@app.route('/party/join', methods=['POST'])
def party_join():
    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)
    if uid == False:
        return jsonify({'result':'failed'})
    
    cardid_receive = request.form['cardid_give'] 
    token_receive = request.cookies.get('mytoken')
    userid_receive = validate_token(token_receive)
    
    object_id = ObjectId(cardid_receive)
    party_info = db.party.find_one({ '_id' : object_id })
   
    if party_info is None:
        return jsonify({'result' : '해당 모임이 없습니다'})

    state = int(party_info['state']) 
    participants = party_info['participant']

    current_num = len(party_info['participant'])
    max_num = int(party_info['people']) 
   
    if state == 0 and current_num < max_num and userid_receive not in participants:
        db.party.update_one( { "_id" : object_id }, { "$push": { "participant" : userid_receive } } );
        after_push = db.party.find_one({ '_id' : object_id })
        current_num = len(after_push['participant'])
        if current_num == max_num:
            db.party.update_one( { "_id" : object_id }, { "$set" : {"state" : "1" } } );
        return jsonify({'result' : 'success'}) 
    else:
        return jsonify({'result' : '모임에 참여할 수 없습니다.'}) 


@app.route('/party/cancel', methods=['POST'])
def party_cancel():
    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)
    if uid == False:
        return jsonify({'result':'failed'})
    
    # return jsonify({'result' : '모임에 참여할 수 없습니다.'}) 
    cardid_receive = request.form['cardid_give'] 
    token_receive = request.cookies.get('mytoken')
    userid_receive = validate_token(token_receive)
    
    object_id = ObjectId(cardid_receive)
    party_info = db.party.find_one({ '_id' : object_id })
    state = int(party_info['state'])

    if party_info is None:
        return jsonify({'result' : '해당 모임이 없습니다'})
        
    participants = party_info['participant']

    if userid_receive not in participants:
        return jsonify({'result' : '해당 참가자가 없습니다'})
    
    db.party.update_one( { "_id" : object_id }, { "$pull": { "participant" : userid_receive } } );
    if state == 1:
        db.party.update_one( { "_id" : object_id }, { "$set": { "state" : "0" } } );
    return jsonify({'result' : 'success'}) 


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)