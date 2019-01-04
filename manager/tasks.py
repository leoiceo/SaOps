#!/usr/bin/python
#_*_coding:utf-8_*_
from __future__ import absolute_import
import celery
from celery.schedules import crontab
from celery import shared_task
from datetime import timedelta
import os

@shared_task
def add(x, y):  
    z = x + y
    print z
    return z


if __name__ == "__main__":
    add(1,3)
