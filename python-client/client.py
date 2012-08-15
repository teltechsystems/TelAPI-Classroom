from flask import Flask, render_template, session, redirect, url_for, request
from common import ClassroomRoles
from werkzeug.routing import BaseConverter

import db
import random
import settings
import security
import simplejson
import urllib, urllib2
import utils

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.context_processor
def node_server_settings():
    return {
        'NODE_SERVER'   : settings.NODE_SERVER
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classroom/<int:classroom_id>/execute', methods=["POST"])
def execute_code_by_session(classroom_id):
    if not 'user_id' in session:
        session['user_id'] = db.insert("INSERT INTO users VALUES()", [])
    
    classroom_user_code = db.fetchrow("SELECT code FROM classroom_user_code WHERE classroom_id = %s AND user_id = %s", [classroom_id, session['user_id']])
    
    if not classroom_user_code:
        return "No code exists for the current user!"
    
    return send_code_execution_request(classroom_user_code['code'])

@app.route('/<int:classroom_id>/<short_code>/execute', methods=["GET", "POST"])
@app.route('/<int:classroom_id>/<short_code>/EXECUTE', methods=["GET", "POST"])
def execute_code_by_short_code(classroom_id, short_code):
    classroom_user_code = db.fetchrow("SELECT code FROM classroom_user_code WHERE classroom_id = %s AND short_code = %s", [classroom_id, short_code])

    if not classroom_user_code:
        return "No code exists for the current user!"

    # return (classroom_user_code['code'], 200, {"Content-type":"text/plain"}, )
    return (send_code_execution_request(classroom_user_code['code']), 200, {"Content-type":"text/plain"}, )

def send_code_execution_request(executable_code):    
    encoded_data = urllib.urlencode({
        'code'  : executable_code
    })
    
    request = urllib2.Request(url="http://%s:%s/" % (settings.SHELL_SERVER['host'], settings.SHELL_SERVER['port'], ), data=encoded_data)
    
    try:
        response = urllib2.urlopen(request).read()
    except urllib2.URLError, e:
        response = "Interpreter server is currently down..."
        
    return response
    
@app.route('/create/classroom', methods=['POST'])
def create_classroom():
    if not 'user_id' in session:
        session['user_id'] = db.insert("INSERT INTO users VALUES()", [])
    
    if 'name' not in request.form:
        return simplejson.dumps({"error":"Invalid classroom name provided!"})
    
    join_characters = "abcdefghijklmnopqrstuvwxyz0123456789"
    join_code_length = 4
    
    join_code = ''.join([join_characters[random.randint(0, len(join_characters) - 1)] for x in range(join_code_length)])
    
    classroom_id = db.insert("INSERT INTO classrooms (name, join_code) VALUES(%s, %s)", [request.form['name'], join_code])
    
    db.insert("INSERT INTO classroom_user_roles (classroom_id, user_id, role) VALUES(%s, %s, %s)", [classroom_id, session['user_id'], ClassroomRoles.TEACHER])
        
    return simplejson.dumps({"classroom_id":classroom_id})

@app.route('/v<regex("[a-zA-Z0-9]{4}"):join_code>')
def classroom_student_join_code(join_code):
    if not 'user_id' in session:
        session['user_id'] = db.insert("INSERT INTO users VALUES()", [])
    
    classroom = db.fetchrow("SELECT * FROM classrooms WHERE join_code = %s", [join_code])
    
    if not classroom:
        return redirect(url_for('.index'))
        
    classroom_user_code = db.get_classroom_user_code(classroom['id'], session['user_id'])

    return render_template('classroom/student.html', 
        user_token          = security.create_user_token(session['user_id'], classroom_id=classroom['id']), 
        classroom           = classroom,
        classroom_user_code = classroom_user_code,
        execution_link      = "%s%s" % (request.host_url[:-1], url_for('.execute_code_by_short_code', classroom_id=classroom['id'], short_code=classroom_user_code['short_code']), )
    )

@app.route('/classroom/<int:classroom_id>')
def classroom_student(classroom_id):
    if not 'user_id' in session:
        session['user_id'] = db.insert("INSERT INTO users VALUES()", [])
        
    classroom = db.fetchrow("SELECT * FROM classrooms WHERE id = %s", [classroom_id])

    if not classroom:
        return redirect(url_for('.index'))
    
    classroom_user_code = db.get_classroom_user_code(classroom['id'], session['user_id'])
    
    return render_template('classroom/student.html', 
        user_token          = security.create_user_token(session['user_id'], classroom_id=classroom['id']), 
        classroom           = classroom,
        classroom_user_code = classroom_user_code,
        execution_link      = "%s%s" % (request.host_url[:-1], url_for('.execute_code_by_short_code', classroom_id=classroom['id'], short_code=classroom_user_code['short_code']), )
    )

@app.route('/classroom/<int:classroom_id>/teacher')
def classroom_teacher(classroom_id):
    if not 'user_id' in session:
        session['user_id'] = db.insert("INSERT INTO users VALUES()", [])

    result = db.fetchrow("SELECT COUNT(*) AS total_entries FROM classroom_user_roles WHERE user_id = %s AND role = %s", [session['user_id'], ClassroomRoles.TEACHER])

    if result['total_entries'] <= 0:
        return redirect(url_for('.classroom_student', classroom_id=classroom_id))
    
    classroom = db.fetchrow("SELECT * FROM classrooms WHERE id = %s", [classroom_id])

    if not classroom:
        return redirect(url_for('.index'))
    
    public_link = "%s%s" % (request.host_url[:-1], url_for('.classroom_student_join_code', join_code=classroom['join_code']), )

    return render_template('classroom/teacher.html', user_token=security.create_user_token(session['user_id'], classroom_id=classroom_id), classroom=classroom, public_link=public_link)

app.secret_key = settings.SECRET_KEY

app.run(**settings.CLIENT_SERVER)