from blog_handler import *
from google.appengine.ext import db
from user import *

class Comment(db.Model):
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    poster_id = db.IntegerProperty(required = True)
    original_post_id = db.IntegerProperty(required = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        self._poster_name = User.get_by_id(self.poster_id, parent = users_key()).name
        return render_str("comment.html", c = self)

class NewComment(BlogHandler):
    def post(self):
        if not self.user:
            self.redirect('/blog/'+original_post_id)
        
        original_post_id = self.request.get('original_post_id')
        content = self.request.get('content')

        if content:
            c = Comment(parent = blog_key(),
                content = content,
                poster_id = self.user.key().id(),
                original_post_id = int(original_post_id))
            c.put()

        self.redirect('/blog/'+original_post_id)

class DeleteComment(BlogHandler):
    def get(self):
        if not self.user:
            self.redirect('/blog')

        comment_id = self.request.get('comment_id')
        if not comment_id:
            self.redirect('/blog')
        
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        original_post_id = comment.original_post_id
        comment.delete()

        self.redirect('/blog/' + str(original_post_id))

class EditComment(BlogHandler):
    def get(self):
        comment_id = self.request.get("comment_id")
        if not comment_id:
            self.redirect('/blog')

        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.error(404)
            return
        self.render("editcomment.html", comment = comment)

    def post(self):
        if not self.user:
            self.redirect('/login')

        content = self.request.get('content')
        comment_id = self.request.get('comment_id')
        
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        c = db.get(key)

        if not c:
            self.error(404)
            return

        if content:
            c.content = content
            c.put()
            self.redirect('/blog/%s' % str(c.original_post_id))
        else:
            error = "content, please!"
            self.render("editcomment.html", comment=c, error=error)
