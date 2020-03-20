#!/bin/bash -ex

archeme generate -c ./source/config.yml -i ./source/architecture.yml -o ./target/architecture.gv
neato -n -T png ./target/architecture.gv -o ./target/architecture.png
