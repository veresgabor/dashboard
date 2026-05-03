#!/usr/bin/env bash

cd "$(dirname "$0")"
nix-shell -p python313 python313Packages.dash python313Packages.pandas python313Packages.plotly --run "python app.py"
