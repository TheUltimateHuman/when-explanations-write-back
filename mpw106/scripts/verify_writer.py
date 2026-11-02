# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["numpy==2.1.3"]
# ///
"""Independent original GPU MPW-106 writer archive and native-report verifier.
Usage: uv run verify_writer.py <immutable-writer-results-commit> <qwen3|granite>.
"""
import sys,json,gzip,base64,hashlib,tempfile,importlib.util
from pathlib import Path
from urllib.request import urlopen
ROOT="https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/"
def fetch(u):return urlopen(u,timeout=90).read()
def sha(b):return hashlib.sha256(b).hexdigest()
def main(commit,model):
    if len(commit)!=40 or any(c not in "0123456789abcdef" for c in commit):
        raise RuntimeError("IMMUTABLE_COMMIT_REQUIRED")
    if model not in ("qwen3","granite"):raise RuntimeError("UNEXPECTED_MODEL")
    prefix=ROOT+commit+"/mpw106/"
    manifest=json.loads(fetch(prefix+"writer/WRITER_MANIFEST.json"))
    info=manifest["models"][model]
    if info["n"]!=64 or len(info["shards"])!=4:
        raise RuntimeError("INCOMPLETE_WRITER_RESULTS")
    rawparts=[]
    for i,anchor in enumerate(info["shards"]):
        encoded=fetch(prefix+f"writer/{model}_shard{i+1:02d}.jsonl.gz.b64").strip()
        compressed=base64.b64decode(encoded,validate=True)
        if anchor.get("compressed_sha256") and sha(compressed)!=anchor["compressed_sha256"]:
            raise RuntimeError("WRITER_GZIP_SHA_MISMATCH")
        raw=gzip.decompress(compressed)
        if sha(raw)!=anchor["raw_sha256"] or len(raw.splitlines())!=16:
            raise RuntimeError("WRITER_RAW_SHA_OR_N_MISMATCH")
        rawparts.append(raw)
    whole=b"".join(rawparts)
    if sha(whole)!=info["combined_raw_sha256"]:
        raise RuntimeError("COMPLETE_WRITER_RAW_MISMATCH")
    screen_commit=info["screen_selection_commit"]
    selection=json.loads(fetch(ROOT+screen_commit+f"/mpw106/selection/{model}.json"))
    source=fetch(prefix+"scripts/independent_writer.py")
    if sha(source)!=manifest["independent_writer_sha256"]:
        raise RuntimeError("INDEPENDENT_WRITER_SOURCE_SHA_MISMATCH")
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"writer.py";p.write_bytes(source)
        spec=importlib.util.spec_from_file_location("independent_writer_mpw106",p)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        original=[json.loads(x) for x in whole.splitlines()]
        report=mod.verify(original,selection,info["model_revision"])
    out={"model":model,"n":len(original),"original_raw_sha256":sha(whole),
         "screen_selection_commit":screen_commit,"writer_archive_commit":commit,
         "independent_verdict":report}
    print("MPW106_WRITER_INDEPENDENT_VERIFIED "+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__":
    if len(sys.argv)!=3:raise RuntimeError("USAGE: SHA MODEL")
    main(sys.argv[1],sys.argv[2])
