import time
import datetime
import pytest
from collections import namedtuple
from marshmallow import Schema, fields, ValidationError
from server.schemas import (
    JSTimestampField,
    MutableField,
    PrimaryKeyRelatedField,
    SelfNestedField,
)

Place = namedtuple('Place', ['name', 'x', 'y'])


class PointSchema(Schema):
    x = fields.Float()
    y = fields.Float()


class PlaceSchema(Schema):
    name = fields.Str()
    coords = SelfNestedField(PointSchema())


class TestSelfNestedField:
    def test_field_serialization(self):
        point = Place('home', 123, 456.1)
        schema = PlaceSchema()
        dumped = schema.dump(point).data
        assert dumped == {"name": "home", "coords": {"x": 123.0, "y": 456.1}}


class TestJSTimestampField:
    def test_parses_current_datetime(self):
        ts = time.time()
        dt = datetime.datetime.fromtimestamp(ts)
        parsed = JSTimestampField()._serialize(dt, None, None)
        assert parsed == int(ts) * 1000
        assert isinstance(parsed, int)

    def test_parses_null_datetime(self):
        assert JSTimestampField()._serialize(None, None, None) is None


User = namedtuple('User', ['username', 'blogposts'])
Blogpost = namedtuple('Blogpost', ['id', 'title'])
Profile = namedtuple('Profile', ['user', 'first_name'])


class UserSchema(Schema):
    username = fields.String()
    blogposts = PrimaryKeyRelatedField(many=True)


class ProfileSchema(Schema):
    user = PrimaryKeyRelatedField('username')
    first_name = fields.String()


class TestPrimaryKeyRelatedField:
    @pytest.fixture(autouse=True)
    def load_data(self):
        self.blogposts = [
            Blogpost(1, 'aaa'),
            Blogpost(2, 'bbb'),
            Blogpost(3, 'ccc'),
        ]
        self.user = User('test', self.blogposts)
        self.profile = Profile(self.user, 'david')

    def serialize(self, obj=None, schema=UserSchema):
        return schema(strict=True).dump(obj or self.user).data

    def test_many_id(self):
        assert self.serialize() == {"username": "test",
                                    "blogposts": [1, 2, 3]}

    def test_many_title(self):
        class UserSchemaWithTitle(UserSchema):
            blogposts = PrimaryKeyRelatedField('title', many=True)
        data = self.serialize(schema=UserSchemaWithTitle)
        assert data == {"username": "test", "blogposts": ['aaa', 'bbb', 'ccc']}

    def test_single(self):
        assert self.serialize(self.profile, ProfileSchema) == {
            "user": "test",
            "first_name": "david"
        }

    def test_single_with_none_value(self):
        assert self.serialize(Profile(None, 'other'), ProfileSchema) == {
            "user": None,
            "first_name": "other"
        }


Blogpost2 = namedtuple('Blogpost', ['id', 'title', 'user'])


class Blogpost2Schema(Schema):
    id = fields.Integer()
    title = fields.String()
    user = MutableField(fields.Nested(UserSchema, only=('username',)),
                        fields.String())

class TestMutableField:

    serialized_data = {"id": 1, "title": "test", "user": {"username": "john"}}
    loaded_data = {"id": 1, "title": "test", "user": "john"}

    @pytest.fixture(autouse=True)
    def load_data(self):
        self.user = User('john', [])  # I don't care for the user's blogposts
        self.blogpost = Blogpost2(1, 'test', self.user)

    def serialize(self, obj=None, schema=Blogpost2Schema):
        return schema(strict=True).dump(obj or self.blogpost).data

    def load(self, data, schema=Blogpost2Schema):
        return schema(strict=True).load(data).data

    def test_serialize(self):
        assert self.serialize() == self.serialized_data

    def test_deserialize(self):
        assert self.load(self.loaded_data) == self.loaded_data

    def test_deserialize_fails(self):
        with pytest.raises(ValidationError):
            self.load(self.serialized_data)