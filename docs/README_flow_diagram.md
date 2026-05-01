# Flow diagram (PNG)

This repo includes a Graphviz source file at `docs/flow_diagram.dot`.

To render the PNG locally:

```bash
# macOS
brew install graphviz

# Ubuntu / EC2
sudo apt-get update
sudo apt-get install -y graphviz

# then (from repo root)
python scripts/render_flow_diagram.py
```

Output: `docs/flow_diagram.png`

