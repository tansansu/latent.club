#!/bin/bash
cd /home/revlon/Codes/Web/latent_info/
python3 Execute_site.py
cd /home/revlon/Codes/Web/hugo_latent-info
hugo --theme=hugo-material-docs
cd /home/revlon/Codes/Web/latent-info.github.io
sudo git add --all
sudo git commit -m 'regular uploading of articles'
expect <<EOF
spawn bash -c "git push origin master"
sleep 0.5
expect -re "Username"
send "latent-info\r"
expect -re "Password"
send "pty107jjj\r"
expect eof
EOF
