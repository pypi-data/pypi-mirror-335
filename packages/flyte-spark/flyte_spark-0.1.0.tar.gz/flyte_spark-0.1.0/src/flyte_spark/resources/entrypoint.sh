#!/bin/bash
export SPARK_EXECUTOR_POD_IP="[${SPARK_EXECUTOR_POD_IP}]"
exec /opt/entrypoint_old.sh "$@" 