from flask import Flask, request

import __builtin__
import base64
import multiprocessing
import new
import settings
import sys
import os
import StringIO
import traceback

app = Flask(__name__)

# def execute_program(program):
#     statement_module = new.module('__main__')
#     
#     statement_module.__builtins__ = __builtin__
#         
#     program = request.form['code']
#     
#     buffer = StringIO.StringIO()
#     
#     sys.stdout = buffer
#     
#     # Import the lib for helper functions
#     import lib
#     
#     os.chroot("/Users/bryanmoyles/Projects/TelAPIClassroom/python-shell/jail")
#     
#     try:
#         compiled = compile(program, "<string>", "exec")
#     
#         exec compiled in statement_module.__dict__
#     except Exception, e:
#         # Write the traceback to the buffer :)
#         traceback.print_exc(file=buffer)
#     
#     sys.stdout = sys.__stdout__
#     
#     response = buffer.getvalue()
#     
#     if not len(response):
#         response = "No print statements were provided!"
#     
#     return response

@app.route('/', methods=["POST"])
def execute():
    if 'code' not in request.form:
        return 'Invalid code provided!\n'
    
    # pool = multiprocessing.Pool(processes=1)
    # 
    # output = pool.apply(execute_program, (request.form['code'], ))
    # 
    # pool.close()
    # 
    # return output
        
    statement_module = new.module('__main__')
    
    statement_module.__builtins__ = __builtin__
        
    program = request.form['code']
    
    buffer = StringIO.StringIO()
    
    sys.stdout = buffer
    
    try:
        compiled = compile(program, "<string>", "exec")
    
        exec compiled in statement_module.__dict__
    except Exception, e:
        # Write the traceback to the buffer :)
        traceback.print_exc(file=buffer)
    
    sys.stdout = sys.__stdout__
    
    response = buffer.getvalue()
    
    if not len(response):
        response = "No print statements were provided!"
    
    return response

app.run(**settings.SHELL_SERVER)