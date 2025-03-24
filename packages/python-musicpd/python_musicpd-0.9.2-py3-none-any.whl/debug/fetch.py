#!/usr/bin/env python3
# coding: utf-8

import sys
import musicpd


def main():
    cli = musicpd.MPDClient()
    cli.connect(host='hispaniola.lan')
    cli.password('otivni')
    track = 'entrant/The Cure/1986-Staring at the Sea_ The Singles/01-The Cure - Killing an Arab.mp3'
    #track = "muse/50 Cent/2003-Get Rich or Die Tryin'-0694935442-FLAC/01-50 Cent - Intro.flac"
    track = 'muse/Alt-J/2012-An Awesome Wave/01-Alt-J - Intro.flac'
    track = 'muse/Amon Tobin/2002-Out, From Out Where/01-Amon Tobin - Back From Space.mp3'
    with open('/tmp/cover', 'wb') as cover:
        rpict = cli.readpicture(track, 0)
        received = int(rpict.get('binary'))
        size = int(rpict.get('size'))
        cover.write(rpict.get('data'))
        while received < size:
            rpict = cli.albumart(track, received)
            cover.write(rpict.get('data'))
            print('got next %s' % rpict.get('binary'))
            received += int(rpict.get('binary'))
            if rpict.get('binary') == '0':
                print(cli.stats())
                cli.disconnect()
                return
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
