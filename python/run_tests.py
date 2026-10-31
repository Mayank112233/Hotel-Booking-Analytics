"""Run the local suite and retain its actual output and exit status."""
import subprocess
import sys
from common import ROOT

def main():
    command=[sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v']
    result=subprocess.run(command,capture_output=True,text=True)
    output=result.stdout+result.stderr
    (ROOT/'reports/test_results.txt').write_text(output,encoding='utf-8')
    print(output)
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
