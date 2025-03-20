# Copyright (c) 2023 and later Renault S.A.S.
# Developed by Renault S.A.S. and affiliates which hold all
# intellectual property rights. Use of this software is subject
# to a specific license granted by RENAULT S.A.S.


# VSCode debugger wants a "module", so create a dummy one that directly calls the click entrypoint

# Example of configuration in VSCode:
#  "configurations": [
#    {
#      "name": "Python: Module",
#      "request": "launch",
#      "type": "python",
#      "cwd": "${workspaceFolder}",
#      "module": "gpc",
#      "args": [
#        "--help",
#      ],
#      "justMyCode": true,
#      "stopOnEntry": false,
#      "console": "integratedTerminal",
#      "env": {
#      }
#    }
#  ]
# }

from .cli import main


main()  # pylint: disable=no-value-for-parameter
