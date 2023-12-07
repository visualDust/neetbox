---
sidebar_position: 3
---

# Configure NEETBOX

NEETBOX read workspace configure from `./neetbox.toml` whenever you import NEETBOX package from your code. If there is no such file, try to create one follow [the guide here](/docs/guide/neetcli/workspace).

In the configuration file, there are 4 default feild:
- __logging__ for configuring `neetbox.logging`
- __extension__ for configuring `neetbox.extension`
- __daemon__ for configuring `neetbox.daemon`