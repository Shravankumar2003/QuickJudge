from flask import Flask, request, jsonify
from models import db, User, Problem, TestCase, Submission
from passlib.hash import pbkdf2_sha256
from judge import evaluate_submission
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///judge.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Helper: simple auth stub (replace with JWT or sessions in real projects)
def hash_password(pw):
    return pbkdf2_sha256.hash(pw)

def verify_password(hash_pw, pw):
    return pbkdf2_sha256.verify(pw, hash_pw)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'username exists'}), 400
    user = User(username=data['username'], email=data['email'], password_hash=hash_password(data['password']))
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'user created', 'user_id': user.id})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not verify_password(user.password_hash, data.get('password','')):
        return jsonify({'error': 'invalid credentials'}), 401
    # For simplicity, return user id as token
    return jsonify({'token': str(user.id)})

# Add problem (admin)
@app.route('/problems', methods=['POST'])
def add_problem():
    data = request.json
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({'error': 'missing fields'}), 400
    p = Problem(title=data['title'], description=data['description'], time_limit_ms=data.get('time_limit_ms', 1000))
    db.session.add(p)
    db.session.commit()
    # insert test cases if provided
    for tc in data.get('test_cases', []):
        t = TestCase(problem_id=p.id, input_text=tc['input'], expected_output=tc['output'], is_sample=tc.get('is_sample', False))
        db.session.add(t)
    db.session.commit()
    return jsonify({'message': 'problem created', 'problem_id': p.id})

@app.route('/problems', methods=['GET'])
def list_problems():
    probs = Problem.query.all()
    out = []
    for p in probs:
        out.append({'id': p.id, 'title': p.title, 'description': p.description[:200], 'time_limit_ms': p.time_limit_ms})
    return jsonify(out)

@app.route('/problems/<int:pid>', methods=['GET'])
def get_problem(pid):
    p = Problem.query.get_or_404(pid)
    tcs = [{'id': tc.id, 'input': tc.input_text, 'is_sample': tc.is_sample} for tc in p.test_cases if tc.is_sample]
    return jsonify({'id': p.id, 'title': p.title, 'description': p.description, 'time_limit_ms': p.time_limit_ms, 'sample_testcases': tcs})

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    user_id = data.get('user_id')
    problem_id = data.get('problem_id')
    code = data.get('code')
    if not all([user_id, problem_id, code]):
        return jsonify({'error': 'missing fields'}), 400
    # create submission record
    sub = Submission(user_id=user_id, problem_id=problem_id, code=code, status='PENDING')
    db.session.add(sub)
    db.session.commit()

    # fetch problem test cases (non-sample for evaluation)
    tcs = TestCase.query.filter_by(problem_id=problem_id, is_sample=False).all()
    tc_list = [{'input_text': tc.input_text, 'expected_output': tc.expected_output} for tc in tcs]

    # evaluate (synchronously here; can be moved to a worker)
    res = evaluate_submission(code, tc_list, time_limit_ms=Problem.query.get(problem_id).time_limit_ms)

    sub.status = res['final_status']
    sub.time_ms = res['max_time_ms']
    sub.result = str(res['results'])
    db.session.commit()

    return jsonify({'submission_id': sub.id, 'status': sub.status, 'time_ms': sub.time_ms, 'details': res['results']})

@app.route('/submissions/<int:sid>', methods=['GET'])
def get_submission(sid):
    sub = Submission.query.get_or_404(sid)
    return jsonify({'id': sub.id, 'user_id': sub.user_id, 'problem_id': sub.problem_id, 'status': sub.status, 'time_ms': sub.time_ms, 'result': sub.result})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
