#!/usr/bin/env sh

if command -v pytest >/dev/null 2>&1 ; then
    pytest --cov=warawara --cov-report=html
else
    python3 -m unittest --verbose
fi
