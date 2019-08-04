#!/usr/bin/env bash -x

sudo apt-get update && sudo apt-get install -y python3-pip mosh byobu git vim

wget https://my.kix.co.il/pub/.vimrc -O .vimrc

git clone https://github.com/gmarik/Vundle.vim.git ~/.vim/bundle/Vundle.vim

git clone https://github.com/phntom/fused_home.git

sudo pip3 install -r fused_home/requirements.txt

crontab fused_home/crontab.txt
