#!/bin/bash

# local docker test 

# init
pushd "$(dirname $0)" > /dev/null

docker build --rm -t lang-detect .

tmp_dir=".test"

if [ -d "$(pwd)/$tmp_dir" ]; then
  rm -rf $(pwd)/$tmp_dir
fi
mkdir -p $(pwd)/$tmp_dir

# just list files in cwd
docker run -it  -v $(pwd):/data -w /data --entrypoint ls lang-detect

# extract config
docker run -it  -v $(pwd):/data -w /data lang-detect config -o $tmp_dir/config.json
if [ ! -f "$(pwd)/$tmp_dir/config.json" ]; then
  echo "config.json not saved"
  exit 1
fi

# run lang-detect
docker run -it  -v $(pwd):/data -w /data lang-detect lang-detect -i example/air_quality.pdf -o $tmp_dir/air_quality.pdf
if [ ! -f "$(pwd)/$tmp_dir/air_quality.pdf" ]; then
  echo "lang-detect to pdf failed on example/air_quality.pdf"
  exit 1
fi

docker run -it  -v $(pwd):/data -w /data lang-detect lang-detect -i example/air_quality.pdf -o $tmp_dir/air_quality.txt
if [ ! -f "$(pwd)/$tmp_dir/air_quality.txt" ]; then
  echo "lang-detect to txt failed on example/air_quality.pdf"
  exit 1
fi

popd

echo "SUCCESS"
