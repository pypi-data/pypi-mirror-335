# b15py

Ein Module um das B15F-Board mit Python zu programmieren.

## Installation

`pip install b15py`
oder
```bash
git clone https://www.github.com/mmeiler-dev/b15py
cd b15py
pip install .
```

## Benutzung

Hier folgt ein simples Beispiel von dem Module

```py
from b15py import *

def main():
    drv = B15F.get_instance()
    drv.digital_write(Port0, 255)

if __name__ == "__main__":
    main()
```