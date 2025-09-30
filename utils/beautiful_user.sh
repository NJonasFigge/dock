#! /bin/bash

if [ "$(whoami)" = root ];
    then echo "󱢼";
elif [ "$(whoami)" = jonas ];
    then echo "󰬑";
else
    whoami;
fi
