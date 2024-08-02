
# Scoring API

The script implements a simple scoring service that provides an API. To receive a response, you must send a POST request to the location */method*.

The implementation was carried out in order to study the work of descriptors and metaclasses in Python - validation of request fields occurs at the time of initialization of the request object.


## How to use it

Clone the project

```cmd
  git clone https://github.com/Dormou/scoring_API
 ```

Go to the project directory

```cmd
  cd scoring_API
```

Run the server

```cmd
  python api.py
```

## Requests and responses

### Request structure:

```json
{
    "account": "company name - string, optional, can be empty",
    "login": "user name - string, required, can be empty",
    "method": "method name - string, required, can be empty",
    "token": "token - string, required, can be empty",
    "arguments": "method arguments - dictionary, required, can be empty"
}
```
Request is valid when all fields are valid.

### Response structure
OK:
```json
{
    "code": "status code",
    "response": "method response"
}
```
Error:
```json
{
    "code": "status code",
    "error": "error message"
}
```

### Available methods:
* **online_score**
*arguments:*
```json
{
    "phone": "string or number, length 11, starts with 7, optional, can be empty",
    "email": "string containing @, optionally, can be empty",
    "first_name": "string, optional, can be empty",
    "last_name": "string, optional, can be empty",
    "birthday": "date in DD.MM.YYYY format, no more than 70 years ago, optional, can be empty",
    "gender": "number 0, 1 or 2, optional, can be empty"
}
```
Request is valid when all fields are valid and there is at least one non-empty pair of following: phone - email, first_name - last_name, gender - birthday.

*method response*:
```json
{
    "score": "number"
}
```

* **clients_interests**
*arguments:*
```json
{
    "client_ids": "list of integers, required, not empty",
    "date": "date in DD.MM.YYYY format, optional, can be empty"
}
```
Request is valid when all fields are valid.

*method response*:
```json
{
    "client_id1": ["interest1", "interest2", ...],
    "client2": [ "interest1", ... ],
     ...
}
```


## Running Tests

To run tests, run the following command

```cmd
  python -m unittest discover -s tests -t .
```

