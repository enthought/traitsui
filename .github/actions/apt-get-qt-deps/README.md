# Install Qt dependencies on Ubuntu

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
        toolkit: ['pyqt5']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v2
      - name: Install Qt dependencies for Linux
        uses: ./.github/actions/apt-get-qt-deps
        if: startsWith(matrix.os, 'ubuntu')
```
