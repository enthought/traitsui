import os

from etsdemo.main import main

HERE = os.path.dirname(__file__)

if __name__ == "__main__":
    main(
        [
            {
                "version": 1,
                "name": "TraitsUI Demo",
                "root": os.path.realpath(os.path.join(HERE, "demo")),
            }
        ]
    )
