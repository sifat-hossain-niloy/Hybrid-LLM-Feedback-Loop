import subprocess, tempfile, os, time

def compile_cpp(source: str):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "main.cpp")
        out = os.path.join(d, "a.out")
        open(src, "w").write(source)
        p = subprocess.run(
            ["g++","-std=gnu++17","-O2","-pipe",src,"-o",out],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        ok = (p.returncode == 0)
        return ok, p.stderr, (out if ok else None)

def run_case(binary: str, input_text: str, time_limit_ms: int=2000):
    start = time.time()
    p = subprocess.run([binary], input=input_text, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=time_limit_ms/1000)
    dt = int((time.time()-start)*1000)
    return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "runtime_ms": dt}
