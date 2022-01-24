# Get our code
token=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
url=https://codeload.github.com/EY-Data-Science-Program/2022-Better-Working-World-Data-Challenge/zip/main
try wget --header "Authorization:  token $token" $url -O /tmp/archive.zip
unzip /tmp/archive.zip
codepath=/home/frog/challenge
mv 2022-Better-Working-World-Data-Challenge-main $codepath
chown -R frog:frog $codepath
