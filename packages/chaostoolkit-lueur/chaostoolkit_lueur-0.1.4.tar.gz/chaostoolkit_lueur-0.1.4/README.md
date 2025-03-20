# Chaos Toolkit Extension Template

[![Version](https://img.shields.io/pypi/v/chaostoolkit-lueur.svg)](https://img.shields.io/pypi/v/chaostoolkit-lueur.svg)
[![License](https://img.shields.io/pypi/l/chaostoolkit-lueur.svg)](https://img.shields.io/pypi/l/chaostoolkit-lueur.svg)

[![Build, Test, and Lint](https://github.com/chaostoolkit-incubator/chaostoolkit-lueur/actions/workflows/build.yaml/badge.svg)](https://github.com/chaostoolkit-incubator/chaostoolkit-lueur/actions/workflows/build.yaml)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-lueur.svg)](https://www.python.org/)

Chaos Toolkit extension to manage [lueur](https://lueur.dev/) network proxy.

## Install

This package requires Python 3.9+

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

[chaostoolkit]: https://github.com/chaostoolkit/chaostoolkit

```console
pip install chaostoolkit-lueur
```

## Usage

```json
{
    "title": "Increase latency by 150ms",
    "description": "n/a",
    "method": [
        {
            "type": "action",
            "name": "run lueur proxy with a normal distribution latency",
            "provider": {
                "type": "python",
                "module": "chaoslueur.actions",
                "func": "run_proxy",
                "arguments": {
                    "proxy_args": "--with-latency --latency-mean 300 --latency-stddev 50 --upstream '*'"
                }
            },
            "background": true
        },
        {
            "type": "action",
            "name": "query remote upstream",
            "provider": {
                "type": "process",
                "path": "curl",
                "arguments": "-I -o /dev/null -s -w \"Connected IP: %{remote_ip}\nTotal time: %{time_total}s\" -x http://localhost:8080 https://www.google.com"
            }
        },
        {
            "type": "action",
            "name": "stop proxy",
            "provider": {
                "type": "python",
                "module": "chaoslueur.actions",
                "func": "stop_proxy"
            }
       }
    ]
}
```

That's it!

Please explore the code to see existing actions.

## Test

To run the tests for the project execute the following:

```console
pdm run test
```

### Formatting and Linting

We use [`ruff`][ruff] to both lint and format this repositories code.

[ruff]: https://github.com/astral-sh/ruff

Before raising a Pull Request, we recommend you run formatting against your
code with:

```console
pdm run format
```

This will automatically format any code that doesn't adhere to the formatting
standards.

As some things are not picked up by the formatting, we also recommend you run:

```console
pdm run lint
```

To ensure that any unused import statements/strings that are too long, etc.
are also picked up.

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please, fork this project, make your changes following the
usual code style, sprinkling with tests and submit a PR for
review.

To contribute to this project, you will also need to install [pdm][].

[pdm]: https://pdm-project.org/en/latest/
