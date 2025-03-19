# easy-serverless

Easy serverless is a set of tools designed to make writing serverless code easier. So far its just a wrapper for AWS 
Lambda functions, designed to make writing them easier and more pythonic.

### Simple Example
#### my_function.py
```python
def hello(first_name, last_name=""):

    message = f'Hello {first_name} {last_name}!'.strip()
    return {'message': message}
```

#### lambda_function.py
```python
from easy_serverless.aws import easy_lambda
from my_function import hello
lambda_handler = easy_lambda(hello, unpack_lists=True)
```

Just point AWS to the `lambda_function.lambda_handler` variable (the default for Lambdas created in the console) and that's it. 
`easy_lambda` handles unpacking the arguments from the lambda event into your function so you don't have to write 
a bunch of boilerplate code to handle it. The following inputs to the lambda function will all work correctly.

```
{"first_name": "John", "last_name": "Doe"}
>>> {"message": "Hello John Doe!"}

{"first_name": "John"}
>>> {"message": "Hello John!"}

"John"
>>> {"message": "Hello John!"}

["John", "Doe"]
>>> {"message": "Hello John Doe!"}
```

### Complex example

OK, so how does this work when you want to reuse objects between AWS Lambda invokes?
We recommend the following code structure.

### my_class.py
```python

class DatabaseInterface:
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def get(self, first_name, last_name=""):
        # code goes here
        ...
```

#### lambda_function.py
```python
import os
from somewhere import make_engine
from easy_serverless.aws import easy_lambda
from my_function import DatabaseInterface

engine = make_engine(os.environ.get("DB_CONN_STR"))

interface = DatabaseInterface(engine)

lambda_handler = easy_lambda(interface.get, unpack_lists=True)
```
By keeping all object instances to `lambda_function.py` we have found it much easier to run tests on the code you care 
about, without having to `mock` a bunch of stuff.


## Coming Soon

* Async functions. We plan to make easy_lambda handle all the boilerplate for running Async code.
* EasyRouter. An extension to easy_lambda to work with the AWS APIGateway integration for AWS Lambda.
* Other languages. node is next on the list.
* Other clouds. Azure Functions and Cloud Functions. (long way off)



