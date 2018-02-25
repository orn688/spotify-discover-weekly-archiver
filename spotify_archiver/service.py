# -*- coding: utf-8 -*-


def handler(event, context):
    e = event.get('e')
    pi = event.get('pi')
    return e + pi
