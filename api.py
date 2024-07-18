#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import hashlib
import uuid
from datetime import datetime, timedelta
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from weakref import WeakKeyDictionary
import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class FieldsOwner(type):
    def __new__(cls, name, bases, attrs):
        for n, v in attrs.items():
            if isinstance(v, Field):
                v.label = n
        return super().__new__(cls, name, bases, attrs)


class Field(object):
    def __init__(self, required=False, nullable=True):
        self.label = None
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if value is None or isinstance(value, (dict, list)) and len(value) == 0:
            if self.nullable:
                self.data[instance] = value
            else:
                raise ValueError(f"Field {self.label} is not nullable.")
        else:
            self.validate(value)
            self.data[instance] = value

    def validate(self, value):
        pass


class CharField(Field):
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f'Field {self.label} must be a string.')


class EmailField(CharField):
    def validate(self, value):
        super().validate(value)
        if '@' not in value:
            raise ValueError(f'Field {self.label} has invalid format.')


class PhoneField(Field):
    def validate(self, value):
        if not isinstance(value, (str, int)):
            raise TypeError(f'Field {self.label} must be a string or an integer.')
        if len(str(value)) != 11 or not str(value).startswith('7'):
            raise ValueError(f'Field {self.label} has invalid format.')


class DateField(Field):
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f'Field {self.label} must be a string.')
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError(f'Field {self.label} has invalid format (must be DD.MM.YYYY).')


class BirthDayField(DateField):
    def validate(self, value):
        super().validate(value)
        date = datetime.strptime(value, '%d.%m.%Y')
        delta = timedelta(70 * 365)
        if datetime.now() - delta > date:
            raise ValueError(f'Field {self.label} has unacceptable value (must be not earlier than 70 years ago)')


class GenderField(Field):
    def validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f'Field {self.label} must be an integer.')
        if value not in GENDERS:
            raise ValueError(f'Field {self.label} has unacceptable value (must be one of {list(GENDERS.keys())})')


class ClientIDsField(Field):
    def validate(self, value):
        if not isinstance(value, list) or any(not isinstance(item, int) for item in value):
            raise TypeError(f'Field {self.label} must be a list of integers.')


class ArgumentsField(Field):
    def validate(self, value):
        if not isinstance(value, dict):
            raise TypeError(f'Field {self.label} must be a dictionary.')


class Request(metaclass=FieldsOwner):
    def __init__(self, **kwargs):
        self.fields = {}
        for n, v in self.__class__.__dict__.items():
            if isinstance(v, Field):
                if v.required and n not in kwargs:
                    raise ValueError(f'Field {v.label} is required')
                value = kwargs.get(n, None)
                v.__set__(self, value)
                self.fields[n] = value
        super().__init__()


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def get_response(self, ctx, store):
        ctx.update({'nclients': len(self.client_ids)})
        res = {cid: scoring.get_interests(store, cid) for cid in self.client_ids}
        return res


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)
    is_admin = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.validate():
            raise ValueError('Insufficient data to assess, must be at least one pair:'
                             ' (phone - email) or (first name - last name) or (gender - birthday)')

    def validate(self):
        return (self.phone and self.email
                or self.first_name and self.last_name
                or self.gender and self.birthday)

    def get_response(self, ctx, store):
        ctx.update({'has': [n for n, v in self.fields.items() if v]})
        if self.is_admin:
            res = 42
        else:
            res = scoring.get_score(store, **self.fields)
        return {'score': res}


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode()).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode()).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
    methods = {
        "online_score": OnlineScoreRequest,
        "clients_interests": ClientsInterestsRequest
    }
    request_body = MethodRequest(**request['body'])
    if check_auth(request_body):
        try:
            method_request_body = (methods[request_body.method]
                                   (**{**request_body.arguments, 'is_admin': request_body.is_admin}))
            response = method_request_body.get_response(ctx, store)
            code = OK
        except (ValueError, TypeError) as ex:
            logging.exception(f'Invalid request: {ex}')
            response = str(ex)
            code = INVALID_REQUEST
    else:
        code = FORBIDDEN
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception as ex:
            logging.exception(f'Bad request: {ex}')
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, request, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except (TypeError, ValueError) as ex:
                    logging.exception(ex)
                    response = str(ex)
                    code = INVALID_REQUEST
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
