var app = require('http').createServer(handler), 
    io = require('socket.io').listen(app), 
    fs = require('fs');

app.listen(13002);

var mysql      = require('mysql');

var connection = mysql.createConnection({
    host     : 'localhost',
    user     : 'root',
    password : 't3lap1',
    database : 'telapi_classroom'
});

connection.connect();

var classroom_sockets = {}

function handler (req, res) {
    res.writeHead(200);
    res.end("Node Server");
}

function classroom_emit(classroom_id, event, data, classroom_role) {
    for(var socket_id in classroom_sockets[classroom_id]) {
        if(classroom_role && classroom_role != classroom_sockets[classroom_id][socket_id].classroom_role)
            continue;
            
        classroom_sockets[classroom_id][socket_id].emit(event, data);
    }
    
    return true;
}

io.sockets.on('connection', function(socket) {
    socket.classroom_role = 'student';
    socket.name = 'Unknown';

    socket.on('disconnect', function () {
        if(!socket.classroom_id)
            return;
        
        classroom_emit(socket.classroom_id, 'user-disconnect', {
            socket_id       : socket.id,
            name            : socket.name,
            classroom_role  : socket.classroom_role
        });
        
        // Remove the classroom socket
        delete classroom_sockets[socket.classroom_id][socket.id];
    });

    socket.on('user-update', function(data) {
        socket.agent_cookie = data.agent_cookie;
        socket.classroom_role = data.classroom_role;

        if(data.name) {
            connection.query("UPDATE users SET name = ? WHERE id = (SELECT user_id FROM user_tokens WHERE token = ? LIMIT 1)", [data.name, data.user_token], function(err, rows, fields) {
                if (err) throw err;
            });
        }

        connection.query('SELECT u.*, ut.classroom_id FROM users u INNER JOIN user_tokens ut ON ut.user_id = u.id WHERE ut.token = ?', [data.user_token], function(err, rows, fields) {
            if (err) throw err;

            if(!rows.length)
                return;

            user = rows[0];
            
            var new_socket = socket.classroom_id != user.classroom_id;

            io.sockets.sockets[socket.id].classroom_id = socket.classroom_id = user.classroom_id;
            io.sockets.sockets[socket.id].name = socket.name = user.name;
            
            if(typeof classroom_sockets[socket.classroom_id] == "undefined")
                classroom_sockets[socket.classroom_id] = {};
            
            classroom_sockets[socket.classroom_id][socket.id] = socket;

            // User doesn't have a name yet, let's request it
            if(!user.name)
                socket.emit('user-request-name');
            
            if(new_socket) {
                classroom_emit(socket.classroom_id, 'user-connect', {
                    socket_id       : socket.id,
                    name            : socket.name,
                    classroom_role  : socket.classroom_role
                });
                
                // Notify this new socket of all of the current connections
                for(var socket_id in classroom_sockets[socket.classroom_id]) {
                    socket.emit('user-connect', {
                        socket_id       : classroom_sockets[socket.classroom_id][socket_id].id,
                        name            : classroom_sockets[socket.classroom_id][socket_id].name,
                        classroom_role  : classroom_sockets[socket.classroom_id][socket_id].classroom_role
                    });
                }
            }

            classroom_emit(socket.classroom_id, 'user-update', {
                socket_id       : socket.id,
                name            : user.name,
                classroom_role  : socket.classroom_role
            });
        });

        // Restore the previous code
        connection.query("SELECT classroom_id, user_id FROM user_tokens WHERE token = ?", [data.user_token], function(err, rows, fields) {
            if(err) throw err;

            if(!rows.length)
                return;

            var user_token = rows[0];

            connection.query("SELECT code FROM classroom_user_code WHERE classroom_id = ? AND user_id = ?", [user_token.classroom_id, user_token.user_id], function(err, rows, fields) {
                if(err) throw err;

                if(!rows.length)
                    return;

                classroom_user_code = rows[0];

                socket.emit('code-restore', {
                    code    : classroom_user_code['code']
                });
            });
        });
    });

    socket.on('question-asked', function(data) {
        connection.query("SELECT u.name, ut.classroom_id, ut.user_id FROM user_tokens ut INNER JOIN users u ON u.id = ut.user_id WHERE ut.token = ?", [data.user_token], function(err, rows, fields) {
            if(err) throw err;

            if(!rows.length)
                return;
                
            var user_token = rows[0];
            
            connection.query("INSERT INTO classroom_questions (classroom_id, user_id, question, status) VALUES(?, ?, ?, 'unanswered')", [user_token.classroom_id, user_token.user_id, data.question], function(err, result) {
                if(err) throw err;
                
                classroom_emit(user_token.classroom_id, 'question-asked', {
                    classroom_question_id   : result.insertId,
                    user_name               : user_token.name,
                    question                : data.question
                });
            });
        });
    });

    socket.on('code-autosave', function(data) {
        connection.query("SELECT classroom_id, user_id FROM user_tokens WHERE token = ?", [data.user_token], function(err, rows, fields) {
            if(err) throw err;

            if(!rows.length)
                return;
            
            var short_code = '',
                random_chars = "abcdefghijklmnopqrstuvwxyz0123456789";
            
            for(var i = 0; i < 5; i++)
                short_code += random_chars[Math.floor(Math.random() * (random_chars.length - 1))];

            var user_token = rows[0],
                update_vars = [
                    user_token.classroom_id, 
                    user_token.user_id, 
                    short_code,
                    data.value, 
                    data.value
                ];
                
            classroom_emit(user_token.classroom_id, 'code-update', {
                socket_id   : socket.id,
                value       : data.value
            }, 'teacher');

            connection.query("INSERT INTO classroom_user_code (classroom_id, user_id, short_code, code, update_time) VALUES(?, ?, ?, ?, NOW()) ON DUPLICATE KEY UPDATE code = ?, update_time = NOW()", update_vars, function(err, result) {
                if(err) throw err;
            });
        });
    });
});
