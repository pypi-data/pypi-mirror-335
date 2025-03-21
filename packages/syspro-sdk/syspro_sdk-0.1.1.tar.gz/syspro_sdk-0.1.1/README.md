# Syspro SDK
This is a Python SDK for interacting with the Syspro API or Syspro Business Object. It provides a simple and intuitive way to interact with the Syspro API, making it easier to integrate Syspro into your Python applications, or other integrated services.

## Features
- Easy to use
- Supports both the Syspro API and Syspro Business Object
- Supports both XML and JSON formats
- Supports both GET and POST requests
- Supports both single and batch requests
- Supports both single and batch responses
- Supports both single and batch errors

## Pre-requisites
- Python 3.8 or later
- Syspro instance running with proper Business Object licences
- Virtual environment (recommended)

## Installation
Once your virtual environment is activated, you can install the SDK using pip:
```
pip install syspro-sdk
```

## Usage
First, you need to import the SDK client and start an instance of it:
```
from syspro.client import SysproClient
client = SysproClient(
    base_url="https://your-syspro-instance.com",
    operator="your-operator",
    password="your-password",
    company="your-company"
)
```

Once you have an instance of the client, you can start making requests to the Syspro API or Syspro Business Object. Like this : 
```
req = client.requisitions.get(id=123456, line=1)
req.approve()
```

All request from SysproClient needs business object working properly. Please refer to Syspro documentation for more information on how to activate e.net business object. 

## Documentation
The documentation for the SDK is available at [https://syspro-sdk.readthedocs.io](https://syspro-sdk.readthedocs.io).

## License
This project is licensed under a commercial license. See the [LICENSE](LICENSE) file for details.

## Contact
If you have any questions or suggestions, please contact us at [support@heyvince.co](mailto:support@heyvince.co).

## Acknowledgments
This SDK was inspired by the [Syspro API](https://syspro-api.readthedocs.io) and the [Syspro Business Object](https://syspro-bo.readthedocs.io). This SDK is not affiliated with Syspro or any of its subsidiaries.

## Changelog
All notable changes to this project will be documented in the [CHANGELOG](CHANGELOG.md) file.
