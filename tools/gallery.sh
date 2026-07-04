#!/usr/bin/env bash
# Screenshot every main space in both relevant states -> docs/gallery/
set -uo pipefail
cd "$(dirname "$0")/.."
SD=$(mktemp -d)
shot() { # file area state cam
  rm -rf "$SD/g"; tools/shot.sh "docs/gallery/$1" "--area=$2" "--state=$3" "--save-dir=$SD/g" "--shot-cam=$4" --shot-frames=55 2>&1 | tail -1
}
shot porch_spawn.png       gray_cloister glory  "-18.5,1.7,-2,-90,-4,62"
shot west_walk_glory.png   gray_cloister glory  "-10,1.7,10.5,0,-2,60"
shot west_walk_ruin.png    gray_cloister ruin   "-10,1.7,10.5,0,-2,60"
shot garth_glory.png       gray_cloister glory  "-6.5,2.6,7.5,-40,-10,66"
shot garth_ruin.png        gray_cloister ruin   "-6.5,2.6,7.5,-40,-10,66"
shot chandlery.png         gray_cloister glory  "-13.6,1.7,-6.4,55,-6,58"
shot chapter_house.png     gray_cloister glory  "-8,1.8,-13,25,-8,62"
shot bone_garden_ruin.png  gray_cloister ruin   "-3.4,1.9,-13.2,40,-12,62"
shot chapel_glory.png      gray_cloister glory  "2,1.8,13.2,180,-6,60"
shot east_gate_ruin.png    gray_cloister ruin   "10,1.7,3.4,180,-4,60"
shot fog_gate_ruin.png     gray_cloister ruin   "9.8,1.9,-1.4,-25,-4,60"
shot boss_yard_ruin.png    gray_cloister ruin   "14.6,2.4,-2.4,-42,-8,62"
shot yard_cameo_glory.png  gray_cloister glory  "14.6,2.4,-2.4,-42,-8,62"
shot skyline_glory.png     gray_cloister glory  "-6,3.2,6,-52,4,70"
shot porch_facade.png      basilica_porch glory "0,1.7,4.5,0,4,66"
shot terrace_sunset.png    basilica_porch glory "-3,1.6,5.2,160,-10,64"
echo "gallery done"
