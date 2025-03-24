#!/usr/bin/env python3
# coding: utf-8

import musicpd, sys

def main():
    cli = musicpd.MPDClient()
    cli.connect(host='hispaniola.lan')
    cli.password('otivni')
    track = 'muse/Amon Tobin/2002-Out, From Out Where/01-Amon Tobin - Back From Space.mp3'
    track = 'muse/Amon Tobin/2011-ISAM/01-Amon Tobin - Journeyman.mp3'

    rpict = cli.readpicture(track, 0)
    if not rpict:
        print('No embedded picture found', file=sys.stderr)
        sys.exit(1)
    size = int(rpict['size'])
    done = int(rpict['binary'])
    with open('/tmp/cover', 'wb') as cover:
        cover.write(rpict['data'])
        while size > done:
            rpict = cli.readpicture(track, done)
            done += int(rpict['binary'])
            print(f'writing {rpict["binary"]}, done {100*done/size:03.0f}%')
            cover.write(rpict['data'])
    cli.disconnect()

# Script starts here
if __name__ == '__main__':
    main()

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab fileencoding=utf8
