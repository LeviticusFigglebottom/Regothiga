#!/usr/bin/env bash
# Audit sweep -> docs/sweep/. Aims cameras at the places out-of-map leaks and
# misalignments hide: room corners, wall/roof seams, raised-floor edges, the
# terrace lip, and outward views from enclosed rooms (should see the panorama
# or a sealed wall, never void).
set -uo pipefail
cd "$(dirname "$0")/.."
SD=$(mktemp -d)
mkdir -p docs/sweep
shot() { rm -rf "$SD/g"; tools/shot.sh "docs/sweep/$1.png" "--area=$2" "--state=$3" \
  "--save-dir=$SD/g" "--shot-cam=$4" --shot-frames=36 2>&1 | tail -1; echo " -> $1"; }

# --- Gray Cloister (enclosed, flat roof) ---
shot cl_garth_corner  gray_cloister glory "2,1.7,2,-45,26,76"
shot cl_arcade_graze  gray_cloister glory "-7.6,1.7,11,0,1,72"
shot cl_boss_corner   gray_cloister ruin  "20,1.7,-4,-55,16,76"
shot cl_north_corner  gray_cloister glory "-2,1.7,-14,-40,14,74"
shot cl_window_out    gray_cloister glory "-10,1.7,2,90,3,60"
shot cl_roof_seam     gray_cloister glory "16,1.7,-6,90,40,82"

# --- Basilica Nave (enclosed, vaulted, raised gallery floors) ---
shot nave_apse        basilica_nave glory "0,1.7,-26,0,9,66"
shot nave_vault_seam  basilica_nave glory "0,1.7,-14,0,44,82"
shot nave_gallery_edge basilica_nave glory "-9,1.7,-8,-58,22,76"
shot nave_aisle_graze basilica_nave glory "-12,1.7,6,0,0,72"

# --- Ossuary Undercroft (multi-level) ---
shot uc_wland_corner  ossuary_undercroft glory "-20,3.9,0,-110,8,74"
shot uc_eland_corner  ossuary_undercroft glory "21,3.9,-4,-55,8,74"
shot uc_vault_seam    ossuary_undercroft glory "-8,1.6,0,90,40,82"
shot uc_skirt_side    ossuary_undercroft glory "-14,1.5,3.2,92,3,66"

# --- Basilica Porch (semi-open terrace) ---
shot porch_side_edge  basilica_porch glory "6,-1,14,-90,-8,76"
shot porch_far_edge   basilica_porch glory "0,-2,20.5,180,-22,78"
shot porch_portico_c  basilica_porch glory "-4,1.7,-4,-45,20,74"
echo "sweep done"
