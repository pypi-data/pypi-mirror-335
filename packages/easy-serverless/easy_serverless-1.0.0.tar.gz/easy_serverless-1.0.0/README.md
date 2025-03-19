# easy-serverless

Easy serverless is a set of tools designed to make writing serverless code easier. So far its just a wrapper for AWS 
Lambda functions, designed to make writing them easier and more pythonic.

```python
from easy_serverless.aws import easy_lambda

def hello(first_name, last_name=""):

    message = f'Hello {first_name} {last_name}!'.strip()
    return {'message': message}

lambda_handler = easy_lambda(hello, unpack_lists=True)
```

Just point AWS to the `lambda_handler` variable instead of the `hello` function and that's it. 
`easy_lambda` handles unpacking the arguments from the lambda event into your function so you don't have to write 
a bunch of boilerplate code to handle it. The following inputs to the lambda function will all work correctly.

```json
{first_name: "John", last_name: "Doe"}
>>> {'message': "Hello John Doe!"}

{first_name: "John"}
>>> {'message': "Hello John!"}

"John"
>>> {'message': "Hello John!"}

["John", Doe]
>>> {'message': "Hello John Doe!"}
```



