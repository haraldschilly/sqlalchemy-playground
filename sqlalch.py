#!/usr/bin/env python
import sqlalchemy
print sqlalchemy.__version__

###########
#from sqlalchemy.engine import Engine
#from sqlalchemy import event
#
#@event.listens_for(Engine, "connect")
#def set_sqlite_pragma(dbapi_connection, connection_record):
#    cursor = dbapi_connection.cursor()
#    cursor.execute("PRAGMA foreign_keys=ON")
#    cursor.close()
###########

from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')#, echo=True)

print engine.execute("select 1").scalar()

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    dept_id = Column(Integer, ForeignKey('dept.id'))

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
       return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

#################

class Address(Base):
  __tablename__ = 'addresses'
  id = Column(Integer, primary_key=True)
  email = Column(String, nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'))

  user = relationship("User", backref=backref('addresses', order_by=id))

  def __init__(self, email):
    self.email = email

  def __repr__(self):
    return "<Address('%s')>" % self.email

##############

class Dept(Base):
  __tablename__ = 'dept'
  id = Column(Integer, primary_key = True)
  name = Column(String)
  users = relationship("User", backref="dept")

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "<Dept('%s')>" % self.name

##############

Base.metadata.create_all(engine)

ed_user = User('ed', 'Ed Jones', 'edspassword')

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

###

d1 = Dept("floor 1")
d2 = Dept("floor 2")
session.add_all([d1, d2])
session.commit()

for d in session.query(Dept):
  print d.id, d

###

ed_user.dept = d2

session.add(ed_user)
print session.query(User).filter_by(name='ed').first()

new_users = [
    User('wendy', 'Wendy Williams', 'foobar'),
    User('mary', 'Mary Contrary', 'xxg527'),
    User('fred', 'Fred Flinstone', 'blah')]
[ setattr(u, "dept", d1) for u in new_users ]
session.add_all(new_users)

print "dirty:", session.dirty
print "new:", session.new

session.commit()

jack = User('jack', 'Jack Bean', 'gjffdd')
jack.addresses
jack.addresses = [ Address(email='jack@google.com'), Address(email='j25@yahoo.com')]
jack.dept = d1

session.add(jack)
session.commit()

for u in session.query(User).order_by(User.fullname):
  print u
  print u.addresses
  print [ adr.user for adr in u.addresses ]
  print "---"

for name, fullname in session.query(User.name, User.fullname).order_by(User.name):
  print name, fullname

print "ed dept:", ed_user.dept
print "jack dept:", jack.dept
for dname, d in session.query(Dept.name, Dept).all():
  print '%s users: %r' % (dname, d.users)
  for u in d.users:
    if len(u.addresses) > 0:
      print "emails of %s: %s" % (u.name, u.addresses)
