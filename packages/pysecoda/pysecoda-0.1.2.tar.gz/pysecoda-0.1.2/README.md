# PySecoda

This is a basic implementation of a python wrapper for the [Secoda API](https://api.secoda.co/api/schema/redoc/).

Currently, API version 1.0.0 is supported by this wrapper.

Find the full implementation on [Github](https://github.com/Matts52/pysecoda)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `pysecoda`.

```bash
pip install pysecoda
```

## Usage

```python
from pysecoda.pysecoda import PySecoda

API_KEY = 'YOUR_API_KEY'

# Instantiate the PySecoda wrapper
pysecoda = PySecoda(API_KEY)

# Get tags in your Secoda project
tags = pysecoda.tags.get_tags()

...
```

## Modules and Methods

### **Available Modules**  

| Module               | Description                                      |
|----------------------|--------------------------------------------------|
| `charts`            | Manage charts in Secoda                          |
| `collections`       | Handle collections of resources                  |
| `columns`           | Retrieve column-level metadata                   |
| `custom_properties` | Manage custom metadata fields                    |
| `dashboards`        | Work with dashboards                             |
| `databases`         | Fetch and manage database records                |
| `documents`         | Handle Secoda documents                          |
| `events`            | Retrieve event logs                              |
| `glossary`          | Manage glossary terms and definitions            |
| `groups`            | Manage user groups and permissions               |
| `integrations`      | Handle third-party integrations                  |
| `lineage`           | Fetch data lineage information                   |
| `monitors`          | Manage monitoring rules and alerts               |
| `queries`           | Run and retrieve queries                         |
| `questions`         | Handle user-submitted questions                  |
| `resources`         | General resource management                      |
| `schemas`           | Fetch schema information                         |
| `tables`            | Retrieve and manage tables                       |
| `tags`              | Manage tags for resources                        |
| `teams`             | Handle team-related functionalities              |
| `users`             | Manage user accounts and authentication          |


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
