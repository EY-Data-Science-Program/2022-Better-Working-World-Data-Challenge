echo Running script: $0

function try() {
  for i in $(seq 10); do
    $* && break
    sleep 10
  done
}

set -x

# Get our code
try curl github.com
url=https://codeload.github.com/EY-Data-Science-Program/2022-Better-Working-World-Data-Challenge/zip/main
# token=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
# wget --header "Authorization:  token $token" $url -O /tmp/archive.zip
wget $url -O /tmp/archive.zip
unzip /tmp/archive.zip
cd 2022-Better-Working-World-Data-Challenge-main/notebooks
unzip GBIF_Training_Data.zip
rm -r GBIF_Training_Data.zip
cd ../..
codepath=/home/frog/notebooks/challenge
mkdir -p $codepath
mv 2022-Better-Working-World-Data-Challenge-main/notebooks $codepath/
# mv 2022-Better-Working-World-Data-Challenge-main/data $codepath/
sudo chown -R frog:frog $codepath
