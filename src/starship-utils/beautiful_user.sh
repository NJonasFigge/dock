#! /bin/bash

if [ "$(whoami)" = root ];
    then echo -e "󱢼\u200B";
elif [ "$(whoami)" = jonas ];
    then echo -e "󰬑\u200B";
else
    whoami;
fi
