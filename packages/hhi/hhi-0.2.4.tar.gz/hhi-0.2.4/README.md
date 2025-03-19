# hhi 0.2.4

HHI photonics PDK for gdsfactory

## Installation

Use python 3.12. We recommend [VSCode](https://code.visualstudio.com/) as an IDE.

We recommend `uv`

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then you can install with:

```bash
uv venv --python 3.12
uv pip install hhi
```

Then you need to restart Klayout to make sure the new technology installed appears.
