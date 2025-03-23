# OmnivoreAPI: Omnivore API client for Python

**Forked from OmnivoreAPI**

![OmnivoreAPI Icon](https://github.com/Benature/OmnivoreAPI/assets/8194807/d51d462d-4f5a-4031-980e-1faa5ca3f6e0)

This is a Python client for the [Omnivore API](https://omnivore.app).


[![Tests](https://github.com/Benature/OmnivoreAPI/actions/workflows/test.yml/badge.svg)](https://github.com/Benature/OmnivoreAPI/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/omnivore_api.svg)](https://pypi.org/project/omnivore_api/)

## How to use

To use omnivore_api in your Python project, you can follow these steps:

Install the omnivore_api package using pip:

```bash
pip install omnivore_api
```

Import the package into your project and Create a new instance of the client:

```python
from omnivore_api import OmnivoreAPI

omnivore = OmnivoreAPI("your_api_token_here", "your_api_url_here")
```

Use the methods of the OmnivoreAPI class to interact with the Omnivore API. 

```python
profile = omnivore.get_profile()

saved_page = omnivore.save_url("https://www.google.com")
saved_page_with_label = omnivore.save_url("https://www.google.com", ["label1", "label2"])

articles = omnivore.get_articles()

username = profile['me']['profile']['username']
slug = articles['search']['edges'][0]['node']['slug']
articles = omnivore.get_article(username, slug)

subscriptions = omnivore.get_subscriptions()

labels = omnivore.get_labels()
from omnivore_api import CreateLabelInput
omnivore.create_label(CreateLabelInput("label1", "#00ff00", "This is label description"))
```

## Documentation

* Main Omnivore graphql schema is in: [schema.graphql](https://github.com/omnivore-app/omnivore/blob/main/packages/api/src/schema.ts)
* To contribute to this project: [CONTRIBUTING.md](docs/CONTRIBUTING.md)
* To more know about Release process: [RELEASE.md](docs/RELEASE.md), [PYPI.md](docs/PYPI.md)

## Support

If you find this project useful, you can support it by becoming a sponsor. Your contribution will help maintain the project and keep it up to date.

[![GitHub stars](https://img.shields.io/github/stars/Benature/omnivore_api.svg?style=social&label=Star)](https://github.com/Benature/omnivore_api/stargazers)
[![Github Sponsor](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/Benature)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Star History

Check out our growth in the community:

[![Star History Chart](https://api.star-history.com/svg?repos=Benature/OmnivoreAPI&type=Date)](https://star-history.com/#Benature/OmnivoreAPI&Date)
