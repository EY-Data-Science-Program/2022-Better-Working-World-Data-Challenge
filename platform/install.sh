echo Running script: $0

function try() {
  for i in $(seq 10); do
    $* && break
    sleep 10
  done
}

set -x

# Get our code
wget https://github.com/EY-Data-Science-Program/2022-Better-Working-World-Data-Challenge/archive/refs/heads/main.zip -O /tmp/archive.zip
unzip /tmp/archive.zip
codepath=/home/frog/notebooks/challenge
mkdir -p $codepath
mv 2022-Better-Working-World-Data-Challenge-main/notebooks $codepath/
rm -r 2022-Better-Working-World-Data-Challenge-main
chown -R frog:frog $codepath
