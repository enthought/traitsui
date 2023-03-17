# Install Qt dependencies

This action calls `apt-get` to install packages required for running Qt on Ubuntu.

## Inputs

There are no inputs.

## Outputs

There are no outputs.

## Example usage

```yml

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - name: Install Qt dependencies
        uses: ./.github/actions/install-qt-support
```
