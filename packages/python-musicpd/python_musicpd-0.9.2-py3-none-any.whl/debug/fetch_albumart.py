#!/usr/bin/env python3
# coding: utf-8

import sys
import musicpd


def main():
    cli = musicpd.MPDClient()
    #cli.connect(host="/run/user/1000/mpd/socket")
    #track = "Incoming/Eminem/1999-The Slim Shady LP/"
    cli.connect(host='hispaniola.lan')
    cli.password('otivni')
    track = 'muse/Tool/2019-Fear Inoculum/'
    track = 'muse/Amon Tobin/2011-ISAM/01-Amon Tobin - Journeyman.mp3'
    track = 'muse/Les Abonnés Du Rail/Aout 2002/01-Les Abonnés Du Rail - Le Hall Des Gares.oga'
    with open('./cover', 'wb') as cover:
        aart = cli.albumart(track, 0)
        received = int(aart.get('binary'))
        size = int(aart.get('size'))
        cover.write(aart.get('data'))
        while received < size:
            aart = cli.albumart(track, received)
            cover.write(aart.get('data'))
            received += int(aart.get('binary'))
        if received != size:
            print('something went wrong', file=sys.stderr)
    cli.disconnect()


# Script starts here
if __name__ == '__main__':
    try:
        main()
    except musicpd.MPDError as err:
        print(err)

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab fileencoding=utf8
