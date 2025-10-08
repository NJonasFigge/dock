#! /bin/bash

if [ "$(whoami)" = root ];
    then echo -e "󱢼 ";
elif [ "$(whoami)" = jonas ];
    then echo -e "󰬑 ";
else
    whoami;
fi
