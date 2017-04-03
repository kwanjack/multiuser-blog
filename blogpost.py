from blog_handler import *
from google.appengine.ext import db
from user import *
from comment import *

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)    
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    poster_id = db.IntegerProperty(required = True)
    liked_users = db.ListProperty(int)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        self._poster_name = User.get_by_id(self.poster_id, parent = users_key()).name
        return render_str("post.html", p = self)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        comments = Comment.all().order('created').ancestor(blog_key())
        comments.filter("original_post_id =", post.key().id())
        self.render("permalink.html", post = post, comments = comments)

class EditPage(BlogHandler):
    def get(self):
        post_id = self.request.get("post_id")
        if not post_id:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        self.render("editpost.html", post = post)

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        post_id = self.request.get('post_id')
        
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        p = db.get(key)

        if not p:
            self.error(404)
            return

        if subject and content:
            p.subject = subject
            p.content = content
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("editpost.html", post=p, error=error)

class DeletePost(BlogHandler):
    def get(self):
        if not self.user:
            self.redirect('/blog')

        post_id = self.request.get('post_id')
        if not post_id:
            self.redirect('/blog')
        
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        post.delete()
        self.redirect('/blog')

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(),
                subject = subject,
                content = content,
                poster_id = self.user.key().id())

            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class LikeUnlikePost(BlogHandler):
    def get(self):
        # Users not logged in cannot like posts.
        if not self.user:
            self.redirect('/blog')

        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        user_id = self.user.key().id()

        # A user cannot toggle like/dislike on his own post.
        if post.poster_id == user_id:
            self.redirect('/blog')

        # Add user to the list of liked users if the user isn't already there.
        # Otherwise remove it from the list. This toggles Like/Unlike.
        if user_id not in post.liked_users:
            post.liked_users.append(user_id)
        else:
            post.liked_users.remove(user_id)

        post.put()
        self.redirect('/blog/%s' % post_id)