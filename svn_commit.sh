#!/bin/bash
log=`date "+%Y%m%d %H:%M:%S"`
####

#svn st --ignore-externals |grep "?" -v|grep ':' -v|grep -Ev "unversioned|migrations|idea" | sed 's/\?//' |while read line
svn st |grep ".idea|celerybeat.pid|migrations|settings|monitor|uwsgi.pid" -Ev|grep "static/admin" -v|while read line
do
	filepatch=`echo $line|awk '{print $2}'`
    args=`echo $line|awk '{print $1}'`
    if [ $args == "D" ];then
	    svn commit -m "$log add from my macbook"
    else
	    svn add $filepatch --force
	    svn commit -m "$log add from my macbook"
    fi
done
