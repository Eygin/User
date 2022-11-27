from flask import Flask, request, jsonify
from collections import OrderedDict
from passlib.hash import sha256_crypt
from functools import wraps
import MySQLdb
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '99a97e5bbe269870b5764bfb801fbe6a'
cursor = None

def get_db_connection():
    global cursor
    if not cursor:
        db = MySQLdb.connect("127.0.0.1", "root", "", "flask_user", port=3306, autocommit=True)
        cursor = db.cursor()
    return cursor


def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       cursor = get_db_connection()
       if 'Authorization' in request.headers:
           auth = request.headers['Authorization']
           token = str.replace(str(auth),'Bearer ', '')

       if not token:
           return jsonify({'message': 'Token error', 'result':'failed'})
       try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            cursor.execute("SELECT * FROM user WHERE id = %s", (data['id'],))
            user = cursor.fetchone()
            current_user = dict()
            current_user["id"] = user[0]
            current_user["name"] = user[1]
            current_user["email"] = user[2]
            current_user["role"] = user[4]
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator
    
@app.route('/v1/login', methods=['POST'])
def login():
    cursor = get_db_connection()
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    check = cursor.execute(" SELECT * FROM user WHERE email = %s", (email,))
    if not check:
        return jsonify({"data":"Username atau Password salah", "result": "failed"})
    
    list = cursor.fetchone()
    password = sha256_crypt.verify(password, list[3])
    if not password:
        return jsonify({"data":"Username atau Password salah", "result": "failed"})
    
    token = jwt.encode({'id' : list[0], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=120)}, app.config['SECRET_KEY'], "HS256")
    data_user = dict()
    data_user["name"] = list[1]
    data_user["email"] = list[2]
    data_user["role"] = 'Admin' if list[4] == '1' else 'User'
    data_user["token"] = token
    cursor.close()
    return jsonify({"data": data_user, "result": "success"})

@app.route('/v1/register/admin', methods=['POST'])
def register():
    cursor = get_db_connection()
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    password2 = data['confirm_password']

    if password != password2:
        return jsonify({"data": "Password tidak sesuai", "result": "failed"})
    
    check_name = cursor.execute(""" SELECT * FROM user WHERE email = %s OR name = %s""", (email,name,))

    if check_name:
        return jsonify({"data": "Data nama atau email sudah dipakai", "result": "failed"})
    
    password = sha256_crypt.encrypt(password)
    cursor.execute(""" INSERT INTO user(name, email, password, role) VALUES(%s,%s,%s,%s) """, (name, email, password,"1"))
    cursor.close()
    return jsonify({"data": "Berhasil membuat data", "result":"success"}), 200

@app.route('/v1/me', methods=['GET'])
@token_required
def me(current_user):
    return jsonify({"data": current_user, "result":"success"})

@app.route('/v1/user', methods=['GET','POST'])
@app.route('/v1/user/<id>', methods=['GET','PUT', 'DELETE'])
@token_required
def user(current_user, id = None):
    if current_user['role'] == '1':
        cursor = get_db_connection()
        if request.method == 'GET':
            if id:
                cursor.execute(""" SELECT * FROM user WHERE id = %s""", (id,))
                data = cursor.fetchone()
                users = dict()
                users["name"] = data[1]
                users["email"] = data[2]
                users["role"] = 'Admin' if data[4] == '1' else 'User'
            else:
                cursor.execute(""" SELECT * FROM user """)
                data = cursor.fetchall()
                users = []
                for row in data:
                    list = dict()
                    list["name"] = row[1]
                    list["email"] = row[2]
                    list["role"] = 'Admin' if row[4] == '1' else 'User'
                    users.append(list)
            return jsonify({"data": users, "result":"success"})
        elif request.method == 'POST':
            data = request.get_json()
            name = data['name']
            email = data['email']
            password = data['password']
            password2 = data['confirm_password']
            if password != password2:
                return jsonify({"data": "Password tidak sesuai", "result": "failed"})
        
            check_name = cursor.execute(""" SELECT * FROM user WHERE email = %s OR name = %s""", (email,name,))

            if check_name:
                return jsonify({"data": "Data nama atau email sudah dipakai", "result": "failed"})
            
            password = sha256_crypt.encrypt(password)
            cursor.execute(""" INSERT INTO user(name, email, password, role) VALUES(%s,%s,%s,%s) """, (name, email, password,"2"))
            return jsonify({"data": "Berhasil membuat data", "result":"success"})
        elif request.method == 'PUT':
            if id:
                data = request.get_json()
                name = data['name']
                email = data['email']
                password = data['password']
                password2 = data['confirm_password']
                if password != password2:
                    return jsonify({"data": "Password tidak sesuai", "result": "failed"})
                
                cursor.execute(""" SELECT * FROM user WHERE email = %s OR name = %s""", (email,name,))
                data = cursor.fetchone()

                if data[0] != int(id):
                    return jsonify({"data": "Data nama atau email sudah dipakai", "result": "failed"})
                
                password = sha256_crypt.encrypt(password)
                cursor.execute(""" UPDATE user SET name = %s, email = %s, password = %s WHERE id = %s """, (name, email, password, id))

                return jsonify({"data": "Berhasil mengubah data", "result":"success"})
            return jsonify({"data": 'Request invalid', "result": "failed"})
        elif request.method == 'DELETE':
            if id:
                user = cursor.execute(""" DELETE FROM user WHERE id = %s""", (id,))
                if user:
                    return jsonify({"data": 'Data berhasil dihapus', "result": "success"})
                return jsonify({"data": 'Data gagal dihapus', "result": "failed"})
            return jsonify({"data": 'Request invalid', "result": "failed"})
    return jsonify({"data": 'Anda tidak memiliki hak akses', "result": "failed"})
                   
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)