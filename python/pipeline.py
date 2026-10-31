"""One command refresh, paths independent of caller working directory."""
import argparse
import subprocess
import sys
from common import ROOT

def main():
    p=argparse.ArgumentParser(); p.add_argument('--mysql',action='store_true'); p.add_argument('--regenerate',action='store_true',help='Rebuild processed tables from preserved raw source; never synthesize replacement history')
    args=p.parse_args()
    scripts=[['clean_data.py']]
    if args.mysql: scripts.append(['load_database.py'])
    scripts += [['validate_kpis.py']+(['--mysql'] if args.mysql else []),['generate_report.py']]
    for script in scripts: subprocess.run([sys.executable,str(ROOT/'python'/script[0]),*script[1:]],check=True)

if __name__=='__main__': main()
