# Python Wikimedia Enterprise API

This is not the official API for the Wikimedia Enterprise API.

Currently only supports the on-demand API

```python
import wme
creds = await wme.auth.login(username, password)
on_demand = wme.on_demand.OnDemand(creds)
results = await on_demand.lookup("Wikimedia Foundation")
```

## Testing

For testing make a `.env` file with `WME_USERNAME` and `WME_PASSWORD`.

Install the pre-commit hooks with `poetry run pre-commit install` or just run them manually e.g. `poetry run ruff check`
