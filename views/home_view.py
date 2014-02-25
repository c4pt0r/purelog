import tornado.web
import router
import models.post as posts
import time
import json
from views.decorators import check_arguments, need_admin
from utils import get_global_config, set_global_config

@router.route("/")
class IndexViewHandler(tornado.web.RequestHandler):
    def get(self):
        #p = 0 if not self.get_argument('p', None) else int(self.get_argument('p'))
        blogs = posts.get_posts(query={'public':True})
        self.render('posts.html', blogs = blogs,
                title = get_global_config('site_name'))

@router.route('/post')
class PostContentHandler(tornado.web.RequestHandler):
    @check_arguments(['pid'])
    def get(self):
        pid = int(self.get_argument('pid'))
        p = posts.get_posts(query={'pid':int(pid)})
        if len(p) > 0:
            blog = p[0]
            self.render('content.html', blog = blog,
                    title = get_global_config('site_name'))
        else:
            self.finish('no such post')

@router.route('/post/new')
class NewPostHandler(tornado.web.RequestHandler):
    @need_admin
    def get(self):
        self.render('editpost.html', post=posts.empty_post(), is_new=True, title=get_global_config('site_name'))

    @need_admin
    @check_arguments(['title', 'content', 'public'])
    def post(self):
        title = self.get_argument('title')
        author = get_global_config('admin_name', 'admin')
        content = self.get_argument('content')
        brief = self.get_argument('brief', '')
        is_public = True if self.get_argument('public') == '1' else False
        tags = self.get_argument('tags', '').split(',')
        ret = posts.new_post(author, title, tags, content, brief, is_public)
        return self.finish(ret)

@router.route('/post/edit')
class EditPostHandler(tornado.web.RequestHandler):
    @need_admin
    @check_arguments(['pid'])
    def get(self):
        pid = self.get_argument('pid')
        p = posts.get_posts(query={'pid':int(pid)})
        if len(p) > 0:
            post = p[0]
        self.render('editpost.html',pid=post['pid'] ,post=post, is_new = False, title=get_global_config('site_name'))

    @need_admin
    @check_arguments(['pid', 'title', 'content', 'public'])
    def post(self):
        pid = self.get_argument('pid')
        title = self.get_argument('title')
        brief = self.get_argument('brief', '')
        author = 'dongxu'
        content = self.get_argument('content')
        is_public = True if self.get_argument('public') == '1' else False
        tags = self.get_argument('tags', '').split(',')
        ret = posts.update_post(pid, author, title, tags, content, brief, is_public)
        return self.finish(ret)

@router.route('/post/remove')
class RemovePostHandler(tornado.web.RequestHandler):
    @need_admin
    @check_arguments(['pid'])
    def get(self):
        pid = self.get_argument('pid')
        posts.remove_post(pid)
        redirect = self.get_argument('redirect', None)
        if redirect != None and redirect.startswith('/'):
            return self.redirect(redirect)
        return self.finish({'ret':0, 'pid':pid})

@router.route('/admin')
class AdminHandler(tornado.web.RequestHandler):
    @need_admin
    def get(self):
        blogs = posts.get_posts(fields=['title', 'create_ts', 'pid', 'public'])
        self.render('admin.html', blogs=blogs, title=get_global_config('site_name'))

@router.route('/admin/save')
class AdminSaveHandler(tornado.web.RequestHandler):
    @need_admin
    def post(self):
        author = self.get_argument('admin_name')
        site_name = self.get_argument('site_name')
        site_desc = self.get_argument('site_desc')
        set_global_config('admin_name', author)
        set_global_config('site_name', site_name)
        set_global_config('site_desc', site_desc)
        return self.finish({'ret':0})

@router.route('/login')
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('auth.html', title= get_global_config('site_name'))
    def post(self):
        u = self.get_argument('username')
        pwd = self.get_argument('password')
        if u == get_global_config('admin_name') and pwd == get_global_config('admin_pwd'):
            self.set_secure_cookie("is_admin", "1")
        self.redirect('/admin')

