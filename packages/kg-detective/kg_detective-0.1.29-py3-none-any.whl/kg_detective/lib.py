def combine(merged, second):
  first = merged[-1]
  if first[1] > second[0]:
    merged[-1] = (first[0], max(first[1], second[1]), first[2])
  else:
    merged.append(second)
  return merged

def combine_merge(matches):
  _matches = sorted(matches, key=lambda m: m[0])
 
  if len(_matches) <= 1:
    return _matches
  result = [_matches[0]]
  gids = set()
  for m in _matches[1:]: 
    result = combine(result, m)
  return result 

def clean_gid(first, second, gids):
  """clean two tuples, which have three elements respectively 

  Args:
    first (tuple): (start, end, {"gid": gid_x})
    second (tuple): (start, end, {"gid": gid_y})
    gids (set): gids should be cleaned

  Returns:
    int: gid to be cleaned 
  """

  if second[2]["gid"] in gids:
    return second[2]["gid"]
  if first[2]["gid"]==second[2]["gid"]:
    return None
  if first[1] <= second[0] or first[0] >= second[1]:
    return None
  else:
    return second[2]["gid"]



def clean_merge(matches):
  """Make order of a list of tuples, which have four elements

  Args:
    matches (list): [(s1, e1, {"gid": gid1}), (s2, e2, {"gid": gid1}), (s3, e3, {"gid": gid2}), ...]

  Returns:
    list: tuples

  Examples:
    >>> refine([(1, 4, {"gid": 1}), (4, 10, {"gid": 1}), (5, 6, {"gid": 2}), (12, 14, {"gid": 2})])
    [(1, 4, {"gid": 1}), (4, 10, {"gid": 1})]
  """
  _matches = sorted(matches, key=lambda m: m[0])
 
  if len(_matches) <= 1:
    return _matches
  result = [_matches[0]]
  gids = set()
  for m in _matches[1:]: 
    gid = clean_gid(result[-1], m, gids) 
    if gid==None:
      result.append(m)
    else:
      gids.add(gid)
  return result 


def mark(doc, matches):
  result = []
  s = 0
  for start, end, meta in matches:
    if start > s:
      text = doc[s:start].text
      result.append({"text": text, "start": s, "end": start})
    text = doc[start:end].text
    result.append({"text": text, "start": start, "end": end, "meta": meta})
    s = end
  if s < len(doc):
    text = doc[s:].text
    result.append({"text": text, "start": s, "end": len(doc)})
  
  return result
  
