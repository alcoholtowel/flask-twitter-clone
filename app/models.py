from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    profile = db.Column(db.Text, nullable=True)
    icon_url = db.Column(db.String(100), nullable=True)
    header_url = db.Column(db.String(100), nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    tree_id = db.Column(db.Integer, nullable=True)
    tree_position = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attachment_url = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def has_children(self):
        """子ポストが存在するかどうかを返すプロパティ"""
        return Post.query.filter(Post.tree_id == self.tree_id,
                                 Post.tree_position > self.tree_position).count() > 0
    