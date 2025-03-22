# rpmbuilder
Build rpm files from github repos with singleton binaries


## Secrets
Are added in this repo as a gpg encrypted file.
To extract:
```
cd ~/git/mannemsooutions/rpmbuilder
gpg -d secrets.tar.gz.gpg | tar -xv
```
After that your RPM's will be signed ;)...

## Setup docker
I just used:
- arch linux with:
- docker installed, with:
- current user added to docker group
- buildx installed and qemu-user-static enabled

Like:
```
sudo pacman -S docker docker-buildx
sudo usermod -a -G docker $USER
# reboot and log back in
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

## Build the rpms
```
cd ~/git/mannemsooutions/rpmbuilder
make build_rpms
```

## Support
For all rpms that are available from https://github.com/MannemSolutions/rpmbuilder/releases support can be acquired from Mannem Solutions in The Netherlands.

For more information please contact us at www.mannemsolutions.nl/contact
