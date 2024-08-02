from datetime import datetime, timedelta
import unittest
import api
from tests.decorator import cases
import logging


class TestField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.Field(nullable=True)
        cls.not_nullable_field = api.Field(nullable=False)

    def test_field_null_value(self):
        with self.assertRaises(ValueError):
            self.not_nullable_field = None
        self.nullable_field = None
        self.assertIsNone(self.nullable_field)


class TestCharField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.CharField(nullable=True)
        cls.not_nullable_field = api.CharField(nullable=False)

    @cases([2, datetime.now(), [], {}, True])
    def test_char_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases(["", "some_text"])
    def test_char_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, value)
        self.nullable_field = value
        self.assertEqual(self.nullable_field, value)


class TestEmailField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.EmailField(nullable=True)
        cls.not_nullable_field = api.EmailField(nullable=False)

    @cases([2, datetime.now(), [], {}, True])
    def test_email_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases(["", "myemail.com"])
    def test_email_bad_value(self, value):
        with self.assertRaises(ValueError):
            self.not_nullable_field = value
        with self.assertRaises(ValueError):
            self.nullable_field = value

    @cases(["@", "myemail@mail.com"])
    def test_email_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, value)
        self.nullable_field = value
        self.assertEqual(self.nullable_field, value)


class TestPhoneField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.PhoneField(nullable=True)
        cls.not_nullable_field = api.PhoneField(nullable=False)

    @cases([datetime.now(), [], {}, False])
    def test_phone_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases(["", "12345678901", 12345678901, "7999012345", 7999012345])
    def test_phone_bad_value(self, value):
        with self.assertRaises(ValueError):
            self.not_nullable_field = value
        with self.assertRaises(ValueError):
            self.nullable_field = value

    @cases(["79990001234", 79990001234])
    def test_phone_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, value)
        self.nullable_field = value
        self.assertEqual(self.nullable_field, value)


class TestDateField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.DateField(nullable=True)
        cls.not_nullable_field = api.DateField(nullable=False)

    @cases([0, datetime.now(), [], {}, True])
    def test_date_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases(["", "2024.02.12", "12/02/2024", "69.13.2023"])
    def test_date_bad_value(self, value):
        with self.assertRaises(ValueError):
            self.not_nullable_field = value
        with self.assertRaises(ValueError):
            self.nullable_field = value

    @cases(["12.02.2024", "01.01.0001"])
    def test_date_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, datetime.strptime(value, '%d.%m.%Y'))
        self.nullable_field = value
        self.assertEqual(self.nullable_field, datetime.strptime(value, '%d.%m.%Y'))


class TestBirthDayField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.BirthDayField(nullable=True)
        cls.not_nullable_field = api.BirthDayField(nullable=False)

    @cases([0, datetime.now(), [0], {}, True])
    def test_birthday_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases(["", "2024.02.12", "12/02/2024", "69.13.2023", "01.01.1900"])
    def test_birthday_bad_value(self, value):
        with self.assertRaises(ValueError):
            self.not_nullable_field = value
        with self.assertRaises(ValueError):
            self.nullable_field = value

    @cases(["12.02.2024", datetime.strftime(datetime.now() - timedelta(days=365*70-1), '%d.%m.%Y')])
    def test_birthday_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, datetime.strptime(value, '%d.%m.%Y'))
        self.nullable_field = value
        self.assertEqual(self.nullable_field, datetime.strptime(value, '%d.%m.%Y'))


class TestGenderField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.GenderField(nullable=True)
        cls.not_nullable_field = api.GenderField(nullable=False)

    @cases(["male", datetime.now(), [], {}, True])
    def test_gender_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases([-1, 3])
    def test_gender_bad_value(self, value):
        with self.assertRaises(ValueError):
            self.not_nullable_field = value
        with self.assertRaises(ValueError):
            self.nullable_field = value

    @cases([0, 1, 2])
    def test_gender_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, value)
        self.nullable_field = value
        self.assertEqual(self.nullable_field, value)


class TestClientIDsField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.ClientIDsField(nullable=True)
        cls.not_nullable_field = api.ClientIDsField(nullable=False)

    @cases([0, "male", datetime.now(), {}, True])
    def test_ids_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases([["0", 1, 2], []])
    def test_ids_bad_value(self, value):
        with self.assertRaises(ValueError):
            self.not_nullable_field = value
        with self.assertRaises(ValueError):
            self.nullable_field = value

    @cases([[0, 1, 2], [0]])
    def test_ids_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, value)
        self.nullable_field = value
        self.assertEqual(self.nullable_field, value)


class TestArgumentsField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nullable_field = api.ArgumentsField(nullable=True)
        cls.not_nullable_field = api.ArgumentsField(nullable=False)

    @cases([0, "male", datetime.now(), [], True])
    def test_arguments_bad_type(self, value):
        with self.assertRaises(TypeError):
            self.not_nullable_field = value
        with self.assertRaises(TypeError):
            self.nullable_field = value

    @cases([{}, {'key': 'value'}])
    def test_arguments_correct_value(self, value):
        self.not_nullable_field = value
        self.assertEqual(self.not_nullable_field, value)
        self.nullable_field = value
        self.assertEqual(self.nullable_field, value)


logging.disable(logging.ERROR)
if __name__ == "__main__":
    unittest.main()
