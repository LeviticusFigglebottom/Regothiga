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
shot city_overlook_glory.png basilica_porch glory "0,2.3,3,180,7,80"
shot city_overlook_ruin.png  basilica_porch ruin  "0,2.3,3,180,11,82"

# pass 4: the Basilica Nave
shot nave_vessel_glory.png   basilica_nave glory  "0,1.8,6.5,0,2,64"
shot nave_vessel_ruin.png    basilica_nave ruin   "0,1.8,6.5,0,2,64"
shot nave_chancel_glory.png  basilica_nave glory  "-3,1.9,-17,-15,6,62"
shot nave_boss_ruin.png      basilica_nave ruin   "3,2.2,-16,12,4,62"
shot nave_gallery_glory.png  basilica_nave glory  "-12,6.4,2,-25,-4,66"
shot nave_sexton.png         basilica_nave ruin   "9.4,1.6,-11.4,55,-2,55"
# pass 5: the Ossuary Undercroft
shot undercroft_hall_glory.png ossuary_undercroft glory "0,1.6,8,40,-4,62"
shot undercroft_hall_ruin.png  ossuary_undercroft ruin  "0,1.6,8,40,-4,62"
shot undercroft_watchers.png   ossuary_undercroft glory "5.5,1.7,10.5,25,-4,62"
shot undercroft_bellox.png     ossuary_undercroft ruin  "4,1.9,-2.5,25,-6,62"
echo "gallery done"
