import json
from flask import render_template, request, redirect, session
from app import app
from functools import lru_cache
from app import compare_captions as comparator

# Initialize models

app.secret_key = 'joe'

print('Initializing caption funniness comparator.....')
comparator.initialize()
# comparator.initialize()

@lru_cache()
def load_data():
    with app.open_resource('data.json') as data_file:
        data = json.loads(data_file.read())
    return data

def get_init_options(data):
    session['captions'] = data['captions']
    ret = {}
    for d in session['captions']:
        ret[d] = ' -- '
    return ret

@app.route('/')
def index():
    data = load_data()[0]
    ret = get_init_options(data)
    return render_template('index.html', url=data['img'], options=ret, id=0)


@app.route('/next_cartoon', methods=["POST"])
def next_cartoon():

    next_id = int(request.form['id']) + 1
    data = load_data()

    if int(next_id) >= len(data):
        next_id = 0

    data = data[next_id]
    ret = get_init_options(data)
    return render_template('index.html', url=data['img'], options=ret, id=next_id)


@app.route('/compare_captions', methods=["POST"])
def compare_captions():

    id = int(request.form['id'])
    data = load_data()[id]

    user_caption = request.form['user_caption']
    caps = user_caption.split('\n')
    caps = [c for c in caps if c != '' and c != '\n']
    if 'captions' not in session:
        session['captions'] = caps
    else:
        session['captions'] = session['captions'] + caps

    ranks = comparator.rank_captions(session['captions'], data['contest'])
    ranks = ranks.round(2)

    return render_template('index.html', url=data['img'], options=ranks.to_dict(), id=id)
