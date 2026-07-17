# etlantic-keyring

Local workstation secret provider for [ETLantic](https://github.com/eddiethedean/etlantic)
using the Python [`keyring`](https://keyring.readthedocs.io/) library and OS credential
stores.

```bash
pip install etlantic-keyring
# or: pip install 'etlantic[keyring]'
```

## Wiring

```python
from etlantic import Profile
from etlantic_keyring import create_provider

provider = create_provider(service="etlantic.customer-platform")
runtime.register_secret_provider("keyring", provider)
```

`SecretRef` resolution uses:

- `name` — keyring service name (or falls back to the provider default)
- `key` — keyring username / account name

```toml
[profiles.local.secrets.production-secrets]
provider = "keyring"
service = "etlantic.customer-platform"
```

Fail-closed: missing credentials raise `PipelineExecutionError` at runtime.
