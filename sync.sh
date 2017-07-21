#!/bin/bash
rsync -Pz voteit@scout.voteit.se:~/scout_buildout/var/Data.fs var/Data.fs
rsync -Prz voteit@scout.voteit.se:~/scout_buildout/var/blob var/
rsync -Prz voteit@scout.voteit.se:~/scout_buildout/var/log var/.
