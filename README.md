
# Assignment

## Set up API key

1. Get an api key: https://platform.openai.com/api-keys
2. Create a file in your home directory, such as `my-api-key-file`, add this line:

```
export OPENAI_API_KEY=...
```

## Install and run

Load the API key to an environment variable:

```
source ~/my-api-key-file
```

Install the code:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python Assignment_agent\ template.py
```

## Pushing to EC2

Log into EC2:

```
ssh -i "your-downloaded-key.pem" ubuntu@your-ec2-instance.amazonaws.com
```

Prepare prerequisites for running Python on EC2:

```
sudo apt install python3.12-venv
```

Make a directory for everything to be copied to:

```
mkdir agent
```

In another terminal, copy the files to the EC2 instance:

```
scp -i "your-downloaded-key.pem" ~/my-api-key-file ubuntu@your-ec2-instance.amazonaws.com:/home/ubuntu
scp -i "your-downloaded-key.pem" -r ./* ubuntu@your-ec2-instance.amazonaws.com:/home/ubuntu/agent
```

Then follow the instructions above (Install and run) on the EC2 instance.

# Generate diagram

Prerequisites:

```
brew install graphviz
python3 -m venv .venv
```

Install:

```
source .venv/bin/activate
pip install -r requirements.txt
python scripts/render_flow_diagram.py
```

It will be rendered at docs/flow_diagram.png.
