from flask import Flask, request, abort
app = Flask(__name__)

USERS = {
    None: [1],
    'user': [1, 2, 3, 4, 5],
    'admin': list(range(1, 11)),
}
AUTHENTICATED_USERS = [user for user in USERS if user is not None]

@app.route('/')
def hello():
    user = request.cookies.get('user', None)
    if user not in AUTHENTICATED_USERS:
        user = None
    return '\n<br>\n'.join('<a href="/{record}">Record {record}</a>'.format(record=r) for r in USERS[user])


@app.route('/<int:record_id>')
def show_record(record_id):
    user = request.cookies.get('user', None)
    if user not in AUTHENTICATED_USERS:
        user = None
    if record_id in USERS[user] or record_id % 3 == 0:
        return 'OK\n<br>\nRecord {}'.format(record_id)
    else:
        return abort(404)