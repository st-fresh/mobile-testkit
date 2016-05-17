#!/usr/bin/env bash

ngrep -d any -W byline port 4984 or port 4985 > /tmp/ngrep.txt