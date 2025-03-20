# LNX Edge API Client
##### Written for Python ≥ 3.7

---

## Quickstart

Install using pip:

```shell
pip install api-client-lnx-edge
```

Set the following environment variables:

- `EDGE_API_KEY`: your production API Key (will be looked up automatically on init)
- `EDGE_STAGING_API_KEY`: your staging API Key (also will be looked up automatically on init, requires the use of the `staging=True` flag. see below)


Then you're off:

```python
# import
from edge_api_client import EdgeAPI

# initialize
edge = EdgeAPI()  # uses the environment variable `EDGE_API_KEY`
# or
edge = EdgeAPI(api_key='XXX')  # try not to do this, but if you have to...
# or
edge = EdgeAPI(staging=True)  # uses the environment variable `EDGE_STAGING_API_KEY`, targets the staging backend
# or
edge = EdgeAPI(api_key='XXX', staging=True)  # provide a staging API key and target staging backend

# and you're off:
resp = edge.get_offers()
```


#### Behavioral rules of thumb:

When requesting a report:
  - Pass _date_ (YYYY-MM-DD) strings instead of _datetime_ strings (YYYY-MM-DDTHH:MM:SS.sss) to the `dateRange` field.  # TODO FIX THIS
  - Timezone should _always_ be specified in the request body. `EdgeAPI._get_report(...)` defaults to 
  `America/New_York`, but can be overridden.

---

#### Test script:
```shell script
(venv) > pytest -v
```


Now using marshmallow for data validation on the client-side, allowing users to either specify content as JSON or as 
python arguments for Create Offer endpoint.


Packaging instructions found here: https://packaging.python.org/en/latest/tutorials/packaging-projects/ 
