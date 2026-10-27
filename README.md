# llm-rig

[![tests](https://github.com/decentralizeallengineering/llm-rig/actions/workflows/tests.yml/badge.svg)](https://github.com/decentralizeallengineering/llm-rig/actions/workflows/tests.yml) ![license](https://img.shields.io/badge/license-Apache--2.0-blue)

Shell and Python tools for running local LLM servers inside libvirt VMs, optionally with a GPU passed through.
Keeping the model server in a VM isolates drivers and weights from the host, lets you pin CPUs, and makes a rig easy to rebuild.

The tools read all VM names, addresses, sizes and model files from one config file. No model is bundled or named.

## Install

Needs `virsh`, `virt-install`, `qemu-img`, `genisoimage`, `setfacl`, `ssh`/`scp`, `curl` and Python 3.
Put `bin/` on your `PATH`, generate an ssh key pair at `~/llm-rig/key`, and place an Ubuntu-style cloud image at `~/llm-rig/img/base.img`.

## Configure

```
mkdir -p ~/.config/llm-rig
cp rig.conf.example ~/.config/llm-rig/rig.conf      # VMs, addresses, sizes, llama-server command lines
cp models.list.example ~/.config/llm-rig/models.list  # your own "URL filename" lines
```

Environment variables (`RIG_HOME`, `RIG_CONF`, `RIG_KEY`, `RIG_MODELS`, `RIG_DRIVER`, `RIG_MODEL_NAME`, ...) override the defaults; see the header of each script (`--help`).

## Example

```
fetch-models --llama cpu     # download your listed files and a llama.cpp build into ~/llm-rig/models
rig-up                       # create/start the VMs, copy files, install the llama-server service
rig-status                   # HTTP status of each endpoint
RIG_DRIVER=http://203.0.113.51:8001 qask "Say hello in five words."
rig-down
```

## Tools

- `rig-up`, `rig-down`, `rig-status`, `provision`: VM lifecycle and service install. GPU detach is refused while a host process holds the card.
- `fetch-models`: downloads files from a list you supply.
- `qask`, `tps.py`, `bench.py`: one-shot question, tokens/s check, and a small prompt/generation benchmark.
- `rig-queue`: file-based task queue where the model works through shell/read/write tools inside the VM only.
- `vm/gpuwait.sh`: waits at boot until the passed-through GPU is usable so the server does not fall back to CPU.

## Tests

`sh tests/smoke.sh` checks `--help` on every script and runs `qask` and `tps.py` against a local stub server.

## License

Apache-2.0, see `LICENSE` and `NOTICE`.
