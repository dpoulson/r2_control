#!/bin/bash

for each in `cat $1`; do
   echo $each
   command=`echo $each | awk -F, '{ print $1 }'`
   if [ "$command" == "sleep" ]; then
      length=`echo $each | awk -F, '{ print $2 }'`
      echo "Sleeping $length"
      sleep $length
   fi

   if [ "$command" == "DO" ]; then
      action=`echo $each | cut -c4-`
      echo "Running $action"
      echo $action > /tmp/r2_commands.pipe
   fi
done

