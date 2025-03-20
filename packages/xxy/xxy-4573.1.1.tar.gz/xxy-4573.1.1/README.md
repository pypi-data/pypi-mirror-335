📢🔬 xxy
========

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Release Building](https://github.com/iaalm/xxy/actions/workflows/release.yml/badge.svg)](https://github.com/iaalm/xxy/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/xxy.svg)](https://badge.fury.io/py/xxy)

A financial statement analysis tool.

## Run
```shell
python -m xxy query ./data_example -t "000002.SZ" -d 2022  2023 -n "主营业务收入" "投资收益"
```

### Config file
Config file is under `~/.xxy_cfg.json`.

## Development

### Install dependency
```shell
pip install -e .[dev]
```

### Lint
```shell
make format
```

### Test
```shell
make test
```


### Log critiria
| Level | Verbosity | Frequency | Description |
|-------|-----------|-----------|-------------|
| Critial | Always | Once per run | Can't run anymore |
| Error | Always | Once per run | Can continue run, but this is something unexpected |
| Warning | Always | A few time per run | Can continue run, and it's expected issue |
| Success | -v | At most once per run each code line | User should easy to understand |
| Info | -vv | More than once per run each code line | User should easy to understand |
| Debug | -vvv | At most three per second | Technical details for developers |
| Trace | -vvvv | More than three per second | Easy to know where code is hang |
