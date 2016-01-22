from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from settings import db
except ImportError:
    from settings_local import db


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
            session.close()
            raise
        session.close()
    return go


def admin_only(cls, methods=['post', 'get']):
    def decorator(fn):
        def tmp(self, *args, **kw):
                                    #self.current_user.is_admin()
            if self.current_user and self.current_user.is_admin():
                return fn(self, *args, **kw)
            else:
                self.send_error(status_code=403)
        return tmp

    for method in methods:
        setattr(cls, method, decorator(getattr(cls, method)))
        setattr(cls, method, decorator(getattr(cls, method)))
    return cls
