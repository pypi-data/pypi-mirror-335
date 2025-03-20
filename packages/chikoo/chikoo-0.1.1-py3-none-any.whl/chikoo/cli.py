#!/usr/bin/env python

import argparse
import sys
from . import core

def main():
    parser = argparse.ArgumentParser(description="Quantum computing utility")
    parser.add_argument('--platform', choices=['qiskit', 'cirq', 'braket'], 
                       default='qiskit', help='Quantum platform to use')
    parser.add_argument('--shots', type=int, default=1024, 
                       help='Number of shots to run')
    parser.add_argument('file', help='QASM file to process')
    
    args = parser.parse_args()
    
    result = core.run_qasm(args.file, platform=args.platform, shots=args.shots)
    
    if result and result.get('success'):
        print(f"Successfully ran on {args.platform}")
        print(f"Counts: {result.get('counts', {})}")
    else:
        print(f"Error running on {args.platform}: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()