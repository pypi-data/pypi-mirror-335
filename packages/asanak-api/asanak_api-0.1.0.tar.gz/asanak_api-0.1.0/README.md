A Python API for Asanak
You can use it to interact with the Asanak API.
You can install it using pip:
```
pip install asanak-api
```
create a new instance of the API:
```
from asanak_api import AsanakAPI

api = AsanakAPI(api_key="your_api_key",username="your_username",password="your_password")
```
Notice :
Because Asanak SMS provider uses username and password for authentication, there is an option to use api_key by putting your username and password together and separating them with a comma.
You should provide either api_key or username and password.
```
api_key="your_username,your_password" or api_key="your_api_key"