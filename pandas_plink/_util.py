def last_replace(s, old, new):
    li = s.rsplit(old, 1)
    return new.join(li)
