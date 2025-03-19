# py-shipstation

An unofficial [ShipStation API](https://www.shipstation.com/docs/api/) Python Client

Install

```bash
pip install pyshipstation
```

# Publishing to PyPi

```bash
python -m build
```

```bash
python -m twine upload --repository pypi dist/*
```

# Tests

Run the test suite
```bash
pytest tests/
```
