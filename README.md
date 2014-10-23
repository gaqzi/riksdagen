# Installation

The progress bar package, version 2.3, is tagged as a dev release on
PyPi and as such it'll not be downloaded by default in newer versions
of pip.

So to install and get the correct version a magical invocation needs
to be done which is:

```shell

$ pip install . --upgrade --allow-external progressbar --allow-unverified progressbar
```

After that it's just to run `bin/riksdagen` and follow the
instructions on screen.

The `munch` command only relies on pure Ruby and should be fine as is.
