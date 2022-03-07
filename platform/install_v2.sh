echo Running script: $0

function try() {
  for i in $(seq 10); do
    $* && break
    sleep 10
  done
}

set -x

# Set up challenge directory
codepath=/home/frog/notebooks/challenge
mkdir -p $codepath
cd /home/frog/

# Download repository zipfile from GitHub and unpack
# Note that files in the /tmp folder are purged automatically when the VM is shut down
try curl github.com
url=https://codeload.github.com/EY-Data-Science-Program/2022-Better-Working-World-Data-Challenge/zip/main
wget $url -O /tmp/archive.zip
unzip /tmp/archive.zip

# Unpack training data for consumption
cd 2022-Better-Working-World-Data-Challenge-main/notebooks
unzip GBIF_Training_Data.zip -d training_data
rm -r GBIF_Training_Data.zip    
cd ../..

# Move notebooks folder into final directory (/home/frog/notebooks/challenge/notebooks/... will be the final location of the various jupyter notebooks, training data and requirements.txt used for development requirements).
mv 2022-Better-Working-World-Data-Challenge-main/notebooks $codepath/
sudo chown -R frog:frog $codepath
