#!/bin/bash

status() {
  pid=$(ps -ef | grep padel.py | grep -v grep | awk '{print $2}')
  if [ -z "$pid" ]
    then
      echo "Not running"
    else
      echo "Running with pid $pid"
  fi
}

start() {
  pid=$(ps -ef | grep padel.py | grep -v grep | awk '{print $2}')
  if [ -z "$pid" ]
    then
      SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
      cd $SCRIPT_DIR
      source venv/bin/activate
      nohup python padel.py &
  fi
}

stop() {
  pid=$(ps -ef | grep padel.py | grep -v grep | awk '{print $2}')
  if [ -n "$pid" ]
    then
      kill -9 $pid
  fi
}

update() {
  git reset --hard
  git pull origin main
}

case "$1" in
    'start')
            start
            status
            ;;
    'stop')
            stop
            status
            ;;
    'restart'|'reload'|'reboot')
            stop
            start
            status
            ;;
    'status')
            status
            ;;
    'update'|'upgrade')
            update
            stop
            start
            status
            ;;
    *)
            echo "Usage: $0 { start | stop | restart | status | update }"
            exit 1
            ;;
esac

exit 0
