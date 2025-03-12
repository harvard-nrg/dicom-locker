# DICOM Locker
> [!Note]
> This is a WIP [`pynetdicom`](https://pydicom.github.io/pynetdicom/stable/) implementation
> of [`rossbuddy`](https://github.com/harvard-nrg/rossbuddy).

Receive files over DICOM and sort them in a meaningful way.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation
For best performance, use Python 3.13t ("free-threaded")

```console
pip install git+https://github.com/harvard-nrg/dicom-locker
```

## Usage

```console
dicom-locker --incoming /path/to/incoming --archive /path/to/archive
```

## License

`dicom-locker` is distributed under the terms of the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) license.
