#encoding=utf-8
import db_utils
from db_utils import db, to_dict, init_incr_id, gen_incr_id
import time

def empty_post():
    return {'title': '', 'tags': [], 'content': '', 'public':True, 'pid':-1, 'create_ts':0}

init_incr_id('post')
def gen_post_id():
    return gen_incr_id('post')

def new_post(author, title, tags, content, public=True):
    p = {'author':author, 'title': title, 'tags': tags, 'content': content, 'public': public, 'is_del':0}
    p['create_ts'] = time.time()
    p['pid'] = gen_post_id()
    db.posts.insert(p)
    return {'ret':0, 'pid':p['pid']}

def update_post(pid, author, title, tags, content, public=True):
    p = {'author':author, 'title': title, 'tags': tags, 'content': content, 'public': public}
    p['create_ts'] = time.time()
    p['pid'] = int(pid)
    db.posts.update({'pid': int(pid)}, {'$set': p})
    return {'ret':0, 'pid':p['pid']}

def get_posts(**kv):
    query = kv.get('query', {})
    is_del = kv.get('is_del', 0)
    query['is_del'] = is_del
    if 'fields' in kv:
        field_map = {}.fromkeys(kv['fields'])
        for i in field_map:
            field_map[i] = 1
        return sorted([to_dict(p) for p in db.posts.find(query, field_map)], key=lambda i: -i['create_ts'])
    return sorted([to_dict(p) for p in db.posts.find(query)], key=lambda i: -i['create_ts'])

def remove_post(pid):
    db.posts.update({'pid':int(pid)}, {'is_del': 1})
