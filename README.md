
# Set up API key

1. Get an api key: https://platform.openai.com/api-keys
2. In a file in your home directory, such as `API_KEYS`, add this line:

```
export OPENAI_API_KEY=...
```

Load the API key to an environment variable:

```
source ~/API_KEYS
```

# Install and run

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python Assignment_agent\ template.py
```
