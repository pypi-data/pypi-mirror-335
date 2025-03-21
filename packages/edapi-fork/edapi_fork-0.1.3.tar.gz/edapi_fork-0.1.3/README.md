# edapi

This package is a fork of an (unofficial) integration of the Ed API with Python [https://github.com/smartspot2/edapi](https://github.com/smartspot2/edapi). Since as of now there is no detailed documentation on the HTTP endpoints for the Ed API, I've reverse-engineered the endpoints by snooping through Chrome devtools.

Further, since the Ed API is in beta, the API endpoints can change at any time, and this package may break.

This package is still a work in progress, and currently contains the following features:

- Authenticating through an Ed API token (accessible through [https://edstem.org/us/settings/api-tokens](https://edstem.org/us/settings/api-tokens) or [https://edstem.org/au/settings/api-tokens](https://edstem.org/au/settings/api-tokens))
- Creating threads
- Editing existing threads (both through global ids and through course-specific ids)
- Uploading files to Ed (through direct file upload)
- Get user information
- List existing threads
- Lock and unlock threads

This list may expand as the package is developed further.

## Installation

This package is uploaded to PyPI: [https://pypi.org/project/edapi/](https://pypi.org/project/edapi/); the easiest way to install is with `pip3 install edapi`.

### Building the package

You can also build the package manually; to do so, just run `python3 -m build` in the root directory. This will create a `dist/` folder containing the package wheel, which can be installed via `pip3 install dist/edapi-x.x.x-py3-none.whl`.

## Documentation

Most documentation can be found in `edapi/docs/api_docs.md`; it contains documentation for the API, and also several notes on the HTTP endpoints as I've worked through this package.

## Usage

Your API key can be created through [https://edstem.org/us/settings/api-tokens](https://edstem.org/us/settings/api-tokens) or [https://edstem.org/au/settings/api-tokens](https://edstem.org/au/settings/api-tokens). The API key should be kept secret, and not committed through any version control system.

Insert ed api key in the constrctor. The Ed api endpoint can also be updated by inserting it within the contructor argument. By default its https://edstem.org/api

The following snippet is an example of using the API:

```python
import os
from edapi import EdAPI
from edapi.models.user import User
# load from environment variables
from dotenv import load_dotenv
load_dotenv()

ed = EdAPI(os.getenv("ED_API_TOKEN"))

user_info = ed.get_user_info()
user: User = user_info.get_user_info_summary()

print(f"Hello {user.name}!")
```

Types for all methods are also documented and type hints are used for every method. You can peruse the types in `edapi/edapi/types/`.

### Working with thread content

Ed uses a special XML format to format thread bodies. The various tags are also documented in `edapi/docs/api_docs.md` for your reference.

There are utility methods included to help with the process of creating thread documents through `BeautifulSoup`:

- `new_document()`: creates a new blank document containing the bare XML tags necessary to create a new thread.
  - Returns a new `BeautifulSoup` instance for the new document, along with the root document tag (use the document tag to serialize for the API).
- `parse_document(content: str)`: parses the content string, which holds the XML content of a thread.
  - Similar to `new_document`, returns a new `BeautifulSoup` instance for the parsed document, along with the root document tag.

### install dependencies to run examples scripts

uv pip install -e ".[dev]"
uv run .\examples\getuserinfo.py

### Build package using uv

uv pip install -e ".[build]"
uv build
uv publish

#### publish through github action with tag

git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
