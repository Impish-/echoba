import hashlib

from ming import schema
from ming.odm import FieldProperty
from ming.schema import ObjectId

from toolz.base_classes import BaseMappedClass


class Staff(BaseMappedClass):
    class __mongometa__:
        name = 'staff'
        unique_indexes = [('name',)]

    _id = FieldProperty(schema.ObjectId)
    name = FieldProperty(str)
    role = FieldProperty(str)
    secret_key = FieldProperty(str)

    @staticmethod
    def get_user(username, password):
        auth = Staff.query.get(name=username,
                               secret_key=hashlib.sha512(password + password_salt).hexdigest())
        return auth

    @staticmethod
    def get_user_by_name(username):
        return Staff.query.get(name=username)

    @staticmethod
    def get_user_by_id(id):
        return Staff.query.get(_id=ObjectId(id))

    @staticmethod
    def get_all_users():
        return Staff.query.find().all()

    def create_or_update_user(self, **kwargs):
        mod_boards = kwargs.get('mod_boards', None)
        try:
            kwargs.pop('mod_boards')
        except KeyError:
            mod_boards = []

        user = self.get_user_by_id(kwargs.get('user_id', [None])[0])

        if not user:
            user = Staff()
        if 'password' in kwargs:
            kwargs.update({
                'secret_key': hashlib.sha512(kwargs.get('password')[0] + password_salt).hexdigest(),
            })

        user = self.update_kwargs(user, **kwargs)

        #for board in Board.get_all_boards():
        #    if board.dir in mod_boards or kwargs.get('mod_all_boards', None):
        #        if not user._id in board.moderators:
         #           board.moderators.append(user._id)
            #else:
             #   try:
                    #board.moderators.remove(user._id)
             #   except ValueError:
            #        pass

        user.save()
