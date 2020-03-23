#!/bin/bash -ex

# Style 1

archeme generate -c ./source/style_1/config.yml -i ./source/ott_dvr_subsystem.yml -o ./target/style_1/ott_dvr_subsystem.gv
dot -T png ./target/style_1/ott_dvr_subsystem.gv -o ./target/style_1/ott_dvr_subsystem.png

archeme generate -c ./source/style_1/config.yml -i ./source/service_backend.yml -o ./target/style_1/service_backend.gv
dot -T png ./target/style_1/service_backend.gv -o ./target/style_1/service_backend.png

archeme merge -i ./source/to_combine.yml -o ./target/combined.yml

archeme generate -c ./source/style_1/config.yml -i ./target/combined.yml -o ./target/style_1/combined.gv
dot -T png ./target/style_1/combined.gv -o ./target/style_1/combined.png

# Style 2

archeme generate -c ./source/style_2/config.yml -i ./source/ott_dvr_subsystem.yml -o ./target/style_2/ott_dvr_subsystem.gv
dot -T png ./target/style_2/ott_dvr_subsystem.gv -o ./target/style_2/ott_dvr_subsystem.png

archeme generate -c ./source/style_2/config.yml -i ./source/service_backend.yml -o ./target/style_2/service_backend.gv
dot -T png ./target/style_2/service_backend.gv -o ./target/style_2/service_backend.png

archeme generate -c ./source/style_2/config.yml -i ./target/combined.yml -o ./target/style_2/combined.gv
dot -T png ./target/style_2/combined.gv -o ./target/style_2/combined.png
