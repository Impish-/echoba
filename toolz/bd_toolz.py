from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import db


def get_engine():
    return create_engine('%s://%s:%s@%s/%s' % (db['driver'],
                                               db['username'],
                                               db['password'],
                                               db['host'],
                                               db['bd_name']))


engine = get_engine()


def with_session(fn):
    def go(*args, **kw):
        session = sessionmaker(bind=engine)()
        session.begin(subtransactions=True)
        try:
            ret = fn(session=session, *args, **kw)
            session.commit()
            return ret
        except:
            session.rollback()
            raise
    return go
