import flask
from flask_cors import CORS, cross_origin
import pandas as pd
import sklearn as sk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import feedparser

from flask import Flask
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

documents = {}
good_posts = []
bad_posts = []
similarities = defaultdict(lambda: defaultdict(lambda: {}))
global next_id
next_id = 1

def get_similar_stories(id: str, count: int):
    return None

def rss_entry_to_dict(entry):
    global next_id
    id_to_use = next_id
    next_id += 1
    return {
        'id': id_to_use,
        'published': entry.published,
        'title': entry.title,
        'summary': entry.summary,
        'link': entry.link,
        'read': False
    }


def init_sources():
    feeds = [
        "https://gizmodo.com/rss",
        "https://www.theverge.com/.rss",
        "http://feeds.arstechnica.com/arstechnica/index",
        "https://www.engadget.com/rss.xml"
        #"https://www.strongtowns.org/journal/?format=rss",
        #"https://www.citylab.com/feeds/posts/",
        #"https://reddit.com/r/programming/.rss"
    ]

    for f in feeds:
        data = feedparser.parse(f)
        for entry in data.entries:
            prepared_entry = rss_entry_to_dict(entry)
            documents[prepared_entry['id']] = prepared_entry

    doc_data = pd.DataFrame.from_records([d for d in documents.values()])

    vectorizer = CountVectorizer()
    word_counts = vectorizer.fit_transform(doc_data.title + doc_data.summary)

    for index, row in doc_data.iterrows():
        for index2, row2 in doc_data.iterrows():
            if index==index2:
                continue
            cs = cosine_similarity(word_counts[index], word_counts[index2])
            similarities[row['id']][row2['id']] = float(cs)
            similarities[row2['id']][row['id']] = float(cs)

init_sources()

@app.route('/init')
@cross_origin()
def init():
    init_sources()
    return "Ok"

@app.route('/documents')
@cross_origin()
def posts_next():
    to_send = []
    for post_id in good_posts:
        if len(to_send) == 5:
            break
        post_similarities = [{'id': p[0], 'score': p[1]} for p in similarities[post_id].items()]
        post_similarities.sort(reverse=True, key=lambda p : p['score'])
        for other_post in post_similarities:
            if documents[other_post['id']]['read']==False:
                to_send.append(documents[other_post['id']])
                documents[other_post['id']]['read'] = True
                break;

    general = [v for v in documents.values() if v['read']==False]
    i = 0
    while len(general)>i and len(to_send) != 5:
        to_send.append(general[i])
        documents[general[i]['id']]['read'] = True
        i += 1
    return flask.jsonify(to_send)

@app.route('/similar/<int:post_id>')
@cross_origin()
def similar(post_id: int):
    post_similarities = [{'other_post_id': p[0], 'score': p[1]} for p in similarities[post_id].items()]
    post_similarities.sort(reverse=True, key=lambda p : p['score'])

    return flask.jsonify([
        {'document': documents[p['other_post_id']], 'score': p['score']} for p in post_similarities[:5]])

@app.route('/report/good/<int:post_id>')
@cross_origin()
def report_good(post_id: int):
    good_posts.append(post_id)
    return 'Ok'

@app.route('/report/bad/<int:post_id>')
@cross_origin()
def report_bad(post_id: int):
    bad_posts.append(post_id)
    return 'Ok'