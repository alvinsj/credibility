from datetime import datetime
import time
import math

from sqlalchemy import Column, Integer, DateTime, String, \
    Boolean, ForeignKey, distinct, UniqueConstraint, Text
from sqlalchemy.orm import relationship, backref, object_session

from models import Base
from models.user import User
from models.comment import Comment


class Link(Base):
    __tablename__ = 'Link'

    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    url = Column(String(256))
    user_id = Column(Integer, ForeignKey('User.id'))
    topic_id = Column(Integer, ForeignKey('Topic.id'))
    bias = Column(Integer)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    views = Column(Integer)

    user = relationship("User")
    topic = relationship("Topic")

    def __init__(self, title, url, user_id, topic_id, bias):
        self.title = title
        self.url = url
        self.user_id = user_id
        self.topic_id = topic_id
        self.bias = bias

    def __repr__(self):
        return "<Link('%s','%s', %d, %d)>" \
            % (self.title, self.url, self.user_id, self.topic_id)

    def _get_points(self):
        # hackernews ranking algorithm
        t = time.mktime(datetime.now().timetuple()) \
            - time.mktime(self.created_at.timetuple())
        p = object_session(self).query(
            distinct(LinkVote.user_id)).filter_by(link_id=self.id).count()
        points = (p-1)/math.pow(t+2, 1.8)
        return points
    points = property(_get_points)

    def _get_votes(self):
        return object_session(self).query(
            distinct(LinkVote.user_id)).filter_by(link_id=self.id).count()
    votes = property(_get_votes)

    def _get_comments_count(self):
        return object_session(self).query(
            Comment).filter_by(link_id=self.id).count()

    comments_count = property(_get_comments_count)

    def _get_comments(self):
        comments = object_session(self).query(
            Comment).filter_by(link_id=self.id).all()
        return sorted(
            comments,
            key=lambda comment: comment.points, reverse=True)

    comments = property(_get_comments)


class LinkVote(Base):
    __tablename__ = 'link_votes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    link_id = Column(Integer, ForeignKey('Link.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User")
    link = relationship("Link")

    def __init__(self, link_id, user_id):
        self.link_id = link_id
        self.user_id = user_id

    def __repr__(self):
        return "<LinkVote(%d, %d)>" % (self.link_id, self.user_id)
