from app import app
from models import db, Problem, TestCase

sample = {
    'title': 'Sum Two Integers',
    'description': 'Read two integers and print their sum.',
    'time_limit_ms': 1000,
    'test_cases': [
        {'input': '1 2', 'output': '3', 'is_sample': True},
        {'input': '100 200', 'output': '300'},
        {'input': '-5 5', 'output': '0'}
    ]
}

with app.app_context():
    db.create_all()
    p = Problem(title=sample['title'], description=sample['description'], time_limit_ms=sample['time_limit_ms'])
    db.session.add(p)
    db.session.commit()
    for tc in sample['test_cases']:
        t = TestCase(problem_id=p.id, input_text=tc['input'], expected_output=tc['output'], is_sample=tc.get('is_sample', False))
        db.session.add(t)
    db.session.commit()
    print('Sample problem created with id', p.id)
