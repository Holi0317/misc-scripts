#!/usr/bin/zsh
# This is a template for batch cherry-picking pdf files

set -e

# Change this to path to source pdf
SRC='doc06457720190211162440.pdf'

# Cherry-pick a PDF file and output to directory out/
# $1 - Page range specifier
# $2 - Name of the output file, without file extension
function conv() {
  pages=$1
  name=$2

  file="out/$name.pdf"

  pdfjoin -o $file $SRC $pages
}

conv 1-2 'FF Never Look Back Dead End'
conv 3-6 'Super robot anime collection'
conv 7-8 '銀河鉄道999'
conv 11-16 'Music for a Festival'
conv 17-20 'Crooners Serenade'
conv 25-26 'Pop Culture'
