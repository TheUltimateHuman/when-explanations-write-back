"""Recover exact MPW-102 family bytes from plain Hugging Face job logs.

Recovery verifies per-shard SHA-256 anchors emitted by the job. Log capture must
be complete; failing shards are errors, never silently omitted.
"""
import argparse,base64,gzip,hashlib,json
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()

def recover(lines):
    # Each shard prints PART=0,... with a SHA shared across a shard.
    chunks={}; anchors={}
    for line in lines:
        line=line.strip()
        for marker in ('MPW102_RECORD_SHARD_B64','MPW102_SHARD_HASH'):
            pos=line.find(marker+' ')
            if pos<0:continue
            rec=json.loads(line[pos+len(marker)+1:])
            if marker=='MPW102_RECORD_SHARD_B64':
                key=rec['sha256']
                z=chunks.setdefault(key,{})
                if rec['part'] in z and z[rec['part']]!=rec['data']:
                    raise RuntimeError('DUPLICATE_SHARD_PART_CONFLICT')
                z[rec['part']]=rec['data'];z['total']=rec['total']
            else:
                anchors[rec['part']]=rec
    if len(anchors)!=4 or len(chunks)!=4:
        raise RuntimeError(f'EXPECTED_4_SHARDS_HAVE_{len(anchors)}_ANCHORS_{len(chunks)}_GROUPS')
    ordered=[]
    for idx in range(4):
        anchor=anchors[idx];key=anchor['sha256']
        if key not in chunks:raise RuntimeError(f'SHARD_{idx}_MISSING')
        z=chunks[key];n=z['total']
        if set(z)-{'total'}!=set(range(n)):raise RuntimeError(f'SHARD_{idx}_INCOMPLETE')
        raw=gzip.decompress(base64.b64decode(''.join(z[i] for i in range(n))))
        if sha(raw)!=key:raise RuntimeError(f'SHARD_{idx}_DIGEST_FAILED')
        if len([v for v in raw.splitlines() if v])!=64:raise RuntimeError('SHARD_LENGTH_NOT_64')
        ordered.append(raw)
    content=b''.join(ordered)
    rows=[json.loads(s) for s in content.splitlines() if s]
    if len(rows)!=256 or len(set(r['idx'] for r in rows))!=256:
        raise RuntimeError('ROW_COUNT_OR_INDICES_NOT_256_DISTINCT')
    return content,rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument('logfile');p.add_argument('--output',required=True)
    args=p.parse_args()
    b,rows=recover(Path(args.logfile).read_text().splitlines())
    Path(args.output).write_bytes(b)
    print(json.dumps({'status':'RECOVERED_VERIFIED','n':len(rows),'sha256':sha(b),'output':args.output},indent=2))
if __name__=='__main__':main()
