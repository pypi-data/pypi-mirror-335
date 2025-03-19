# anthrosolui Getting Started

## Installation

To install this library, uses

`pip install anthrosolui`

## Getting Started

### TLDR

TBD

## LLM context files

TBD

### Step by Step

To get started, check out:

1.  Start by importing the modules as follows:

``` python
from fasthtml.common import *
from anthrosolui.all import *
```

2.  Instantiate the app with the anthrosolui headers

``` python
app = FastHTML(hdrs=AnthrosolTheme.epso.headers())

# Alternatively, using the fast_app method
app, rt = fast_app(hdrs=Theme.slate.headers())
```

> *The color option can be any of the theme options available out of the
> box*

From here, you can explore the API Reference & examples to see how to
implement the components. You can also check out these demo videos to as
a quick start guide:
