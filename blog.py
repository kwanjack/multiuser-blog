from google.appengine.ext import db

from blog_handler import *
from comment import *
from user import *
from blogpost import *
from registration import *

import webapp2

class MainPage(BlogHandler):
    def get(self):
        self.redirect('/blog')

class BlogFront(BlogHandler):
    def get(self):
        # Ancestory query allows strongly consistent reads.
        posts = greetings = Post.all().order('-created').ancestor(blog_key())
        self.render('front.html', posts = posts)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/edit', EditPage),
                               ('/blog/delete', DeletePost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/like_toggle', LikeUnlikePost),
                               ('/blog/comment', NewComment),
                               ('/blog/delete_comment', DeleteComment),
                               ('/blog/edit_comment', EditComment)
                               ],
                              debug=True)
