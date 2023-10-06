#!/usr/bin/python
# -*- coding: utf-8 -*-

# util.py: utility functions
#
# Author: Tomi.Mickelsson@iki.fi

import pytz
import datetime
import time
import uuid
import functools
from collections import defaultdict
try:
  basestring
except NameError:  # python3
  basestring = str
from xml.etree import ElementTree as ET
import logging
log = logging.getLogger("util")


# --------------------------------------------------------------------------
# date related common methods

tz_hki = pytz.timezone("Europe/Helsinki")
tz_utc = pytz.utc

def utc2local(utc_dt, tz=tz_hki):
    """Convert UTC into local time, given tz."""

    if not utc_dt:
        return utc_dt

    d = utc_dt.replace(tzinfo=tz_utc)
    return d.astimezone(tz)

def local2utc(local_dt, tz=tz_hki):
    """Convert local time into UTC."""

    if not local_dt:
        return local_dt

    d = local_dt.replace(tzinfo=tz)
    return d.astimezone(tz_utc)

def utcnow():
    """Return UTC now."""
    return datetime.datetime.utcnow()

def generate_token():
    """Generate a random token
    (an uuid like 8491997531e44d37ac3105b300774e08)"""
    return uuid.uuid4().hex

def timeit(f):
    """Decorator to measure function execution time."""
    @functools.wraps(f)
    def wrap(*args, **kw):
        t1 = time.time()
        result = f(*args, **kw)
        t2 = time.time()
        log.info("%r args:[%r, %r] took: %2.4f sec" % \
          (f.__name__, args, kw, t2-t1))
        return result
    return wrap

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d
def dict_to_etree(d):
    def _to_etree(d, root):
        if not d:
            pass
        elif isinstance(d, basestring):
            root.text = d
        elif isinstance(d, dict):
            for k,v in d.items():
                assert isinstance(k, basestring)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, basestring)
                    root.text = v
                elif k.startswith('@'):
                    assert isinstance(v, basestring)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ET.SubElement(root, k))
                else:
                    _to_etree(v, ET.SubElement(root, k))
        else:
            raise TypeError('invalid type: ' + str(type(d)))
    assert isinstance(d, dict) and len(d) == 1
    tag, body = next(iter(d.items()))
    node = ET.Element(tag)
    _to_etree(body, node)
    return ET.tostring(node)

if __name__ == '__main__':

    # quick adhoc tests
    logging.basicConfig(level=logging.DEBUG)

    @timeit
    def myfunc():
        now = utcnow()
        print(now)
        print(utc2local(now))
        time.sleep(1.0)
    myfunc()

