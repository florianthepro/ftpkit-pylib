# ftpkit-pylib

`ftpkit` is the reusable, dependency-free Python foundation for managed Linux web applications. It contains models, validators and safe file primitives, but performs no destructive system actions.

## Install

```sh
python -m pip install .
```

For development:

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Included

- UUID creation and validation
- atomic bytes, text and JSON writes with optional backups
- advisory file locks with timeouts
- safe path validation below configured roots
- IP, domain, port and URL-path validation
- versioned registry and migration helpers
- app manifests, capabilities and management protocol models
- certificate, backup, change-plan, risk and confirmation models
- structured results and structured errors

## Minimal example

```python
from pathlib import Path
from ftpkit import Registry, RegistryStore, new_instance_uuid

store = RegistryStore(Path("/sites/backend/data/registry.json"))
registry = Registry.empty()
instance_id = new_instance_uuid()
store.save(registry)
```

All parsers reject unknown or malformed data unless their API explicitly documents normalization. System mutation, service control, package installation, Caddy and shell operations belong outside this package.

See `CHANGELOG.md` and the public API in `src/ftpkit/__init__.py`.
