#!/bin/sh
#
# Copyright 2008 David Anderson <dave@natulte.net>
#
# Redistribution of this file is permitted under
# the terms of the GNU Public License (GPL) version 2.
#
# Retrieve a local version of jinja2. This is useful if you don't have
# jinja2 available in your distro, or want a self-contained pyweb.

git clone git://github.com/mitsuhiko/jinja2.git jinja2_repos
ln -s jinja2_repos/jinja2 jinja2
git clone git://github.com/qnub/Jinja2-Markdown.git
ln -s Jinja2-Markdown/jinja2_markdown jinja2_markdown
