#!/bin/bash
# Launch script for undertale
# This script will do the following
# 1. Pull latest save from git
# 2. Launch the game
# 3. Commit and push updated save

set -e

git_location="$HOME/.config/UNDERTALE"
bin_location="$HOME/.app/Undertale/runner"
origin=`pwd`

# Step 1: pull saving
echo "Pulling latest save from git"
cd $git_location
git pull

start_time=`date '+%Y-%m-%d %H:%M:%S'`

# Step 2: launch undertale
echo "Starting undertale"
( exec $bin_location  )

# Step 3: Commit and push
cd $git_location
echo "Committing and pushing latest save file"
git add .
git commit -m "Save starting from $start_time"
git push origin master

# Reset working directory
cd $origin
