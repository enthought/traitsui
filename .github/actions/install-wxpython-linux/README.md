# Install prebuilt wxPython wheel for Linux

This action runs pip install wxPython with an attempt to pull prebuilt wheel
from extras.wxpython.org

## Inputs

### `version-range`

**Optional** Version range to be appended to the pip install command. Default
to an empty string. The range will be given to pip, e.g. ">=4,<4.1"

## Outputs

There are no outputs.

## Example usage

```yml
jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Install wxPython on Linux
        uses: ./.github/actions/install-wxpython-linux
          with:
            version-range: '>=4,<4.1'
        if: startsWith(matrix.os, 'ubuntu')

```
