#!/bin/bash

# local docker test 
info() { echo -e "\033[1;35m$1\033[0m"; }

# init
pushd "$(dirname $0)" > /dev/null

img="lang-detect"
pltfm="--platform linux/amd64"

docker build --rm -t $img .

tmp_dir=".test"

if [ -d "$(pwd)/$tmp_dir" ]; then
  rm -rf $(pwd)/$tmp_dir
fi
mkdir -p $(pwd)/$tmp_dir

info "just list files in cwd"
docker run -it  -v $(pwd):/data -w /data --entrypoint ls $img

info "show help"
docker run $pltfm -it -v $(pwd):/data -w /data $img --help

info "extract config"
docker run -it  -v $(pwd):/data -w /data $img config -o $tmp_dir/config.json
if [ ! -f "$(pwd)/$tmp_dir/config.json" ]; then
  echo "config.json not saved"
  exit 1
fi

info "run lang-detect to pdf" 
docker run -it  -v $(pwd):/data -w /data $img lang-detect -i example/air_quality.pdf -o $tmp_dir/air_quality.pdf
if [ ! -f "$(pwd)/$tmp_dir/air_quality.pdf" ]; then
  echo "lang-detect to pdf failed on example/air_quality.pdf"
  exit 1
fi

info "run lang-detect to txt" 
docker run -it  -v $(pwd):/data -w /data $img lang-detect -i example/air_quality.pdf -o $tmp_dir/air_quality.txt
if [ ! -f "$(pwd)/$tmp_dir/air_quality.txt" ]; then
  echo "lang-detect to txt failed on example/air_quality.pdf"
  exit 1
fi

popd

echo "SUCCESS"
