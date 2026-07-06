#!/usr/bin/env bash
# Eye-level validation sweep -> docs/sweep/. Aims cameras at junctions, floor
# seams, stair transitions and roof undersides (where defects hide), not beauty
# framings. Player eye ~1.6 above a y=0 floor; ~4.0 above a y=2.4 landing.
set -uo pipefail
cd "$(dirname "$0")/.."
SD=$(mktemp -d)
mkdir -p docs/sweep
shot() { # name area state cam
  rm -rf "$SD/g"
  tools/shot.sh "docs/sweep/$1.png" "--area=$2" "--state=$3" \
    "--save-dir=$SD/g" "--shot-cam=$4" --shot-frames=34 2>&1 | tail -1
  echo "  -> $1"
}

# ---- Ossuary Undercroft (the most-reported area) ----
shot uc_weststair_down  ossuary_undercroft glory "-19,3.9,0,-90,-24,66"
shot uc_weststair_up    ossuary_undercroft glory "-13,1.5,0,90,10,70"
shot uc_eaststair_up    ossuary_undercroft glory "15.5,1.5,-4,-90,12,70"
shot uc_eaststair_land  ossuary_undercroft glory "23,3.9,-5,90,-8,70"
shot uc_reliquary_stair ossuary_undercroft glory "11.5,1.5,6,-90,10,68"
shot uc_floor_seams     ossuary_undercroft glory "-6,1.1,2,-72,-7,62"
shot uc_hall_glory      ossuary_undercroft glory "3,1.7,0,90,-2,66"
shot uc_hall_ruin       ossuary_undercroft ruin  "3,1.7,0,90,-2,66"
shot uc_ceiling         ossuary_undercroft glory "-8,1.6,0,90,34,72"

# ---- Gray Cloister (garth flat roof + junctions) ----
shot cl_garth_ceiling   gray_cloister glory "0,1.6,0,0,36,72"
shot cl_garth_glory     gray_cloister glory "-2,1.6,6,-30,2,66"
shot cl_garth_ruin      gray_cloister ruin  "-2,1.6,6,-30,2,66"
shot cl_walk_west       gray_cloister glory "-14,1.6,-4,180,0,62"
shot cl_chapel          gray_cloister glory "2,1.6,10,180,2,62"
shot cl_chapterhouse    gray_cloister glory "-6,1.6,-14,0,3,62"
shot cl_boss_yard       gray_cloister ruin  "16,1.7,-6,180,0,64"
shot cl_skyline         gray_cloister glory "-6,2.6,4,-52,8,72"

# ---- Basilica Nave ----
shot nave_down_glory    basilica_nave glory "0,1.7,7,0,2,66"
shot nave_down_ruin     basilica_nave ruin  "0,1.7,7,0,2,66"
shot nave_ceiling       basilica_nave glory "0,1.7,-4,0,36,74"
shot nave_gallery       basilica_nave glory "-12,6.2,2,-25,-3,66"
shot nave_chancel       basilica_nave glory "-2,1.8,-16,0,4,62"
shot nave_aisle         basilica_nave glory "-9,1.6,4,0,0,60"

# ---- Basilica Porch (roofed portico vs open terrace, exposure) ----
shot porch_portico      basilica_porch glory "0,1.7,-3,0,6,66"
shot porch_terrace      basilica_porch glory "0,1.6,4,180,-3,68"
shot porch_stairs_down  basilica_porch glory "0,1.4,7,180,-14,66"
shot porch_terrace_low  basilica_porch glory "0,-1.0,14,180,0,66"
shot porch_facade       basilica_porch glory "0,1.7,5,0,8,66"
echo "sweep done"
