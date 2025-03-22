# pip-show-json
Show JSON metadata about an uninstalled pip package like `apt-get show`.

# Motivation
It is useful to display information about a package which is not yet installed.
This command line utility does this and documents how to do this so that it is easily discoverable

This is basically a wrapper around `curl https://pypi.org/pypi/$PACKAGE/json` which will show you metadata about a package but it is easy to discover and listed in pypi.


# Usage and Installation
```
pipx install pip-show-json
pip-show-json django
```

# About me
I am @readwithai. I sometimes make [productivity tools](https://readwithai.substack.com/p/my-productivity-tools) similar to this. I also am making [tools for reading](https://readwithai.substack.com) sometimes with [Obsidian](https://readwithai.substack.com/p/what-exactly-is-obsidian).

If any of this sounds interesting you can follow me on [X](https://x.com/readwithai) or my [blog](https://readwithai.substack.com).
