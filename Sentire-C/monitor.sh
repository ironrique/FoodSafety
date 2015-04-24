#!/bin/sh

ps auxw | grep start_app.py | grep -v grep > /dev/null
if [ $? != 0 ]
then
	/usr/bin/python2 /home/owapp/Software/start_app.py  > /dev/null
fi

