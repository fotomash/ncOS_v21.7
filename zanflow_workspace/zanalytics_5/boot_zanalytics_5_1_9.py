"""
Helper script to boot ZANALYTICS 5.1.9 in one step:
1. Unpack the ZIP
2. Add unpacked directory to PYTHONPATH
3. Execute the CLI runner
"""
import zipfile
import os
import sys
import subprocess
import argparse


def unpack_zip(zip_path, unpack_dir):
    os.makedirs(unpack_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unpack_dir)
    print(f"✅ ZANALYTICS unpacked to: {unpack_dir}")


def add_to_path(unpack_dir):
    if unpack_dir not in sys.path:
        sys.path.append(unpack_dir)
    print(f"✅ Added to PYTHONPATH: {unpack_dir}")


def run_orchestrator(script_path, input_dir, config_dir, output_dir, strategy_version):
    cmd = [
        sys.executable,
        script_path,
        '--input-dir', input_dir,
        '--config-dir', config_dir,
        '--output-dir', output_dir,
        '--strategy-version', strategy_version
    ]
    print(f"🔄 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def parse_args():
    parser = argparse.ArgumentParser(description='Boot ZANALYTICS 5.1.9')
    parser.add_argument('--zip-path', type=str, default='/mnt/data/zanalytics_5.1.9.zip')
    parser.add_argument('--unpack-dir', type=str, default='/mnt/data/zanalytics_5_1_9_unpacked')
    parser.add_argument('--input-dir', type=str, default='/mnt/data/')
    parser.add_argument('--output-dir', type=str, default='/mnt/data/journal')
    parser.add_argument('--strategy-version', type=str, default='5.1.9')
    return parser.parse_args()


def main():
    args = parse_args()
    unpack_zip(args.zip_path, args.unpack_dir)
    add_to_path(args.unpack_dir)
    # Determine orchestrator script path
    runner_script = os.path.join(args.unpack_dir, 'run_zanalytics_session.py')
    if not os.path.exists(runner_script):
        raise FileNotFoundError(f"Runner script not found: {runner_script}")
    run_orchestrator(
        runner_script,
        args.input_dir,
        os.path.join(args.unpack_dir, 'configs'),
        args.output_dir,
        args.strategy_version
    )

if __name__ == '__main__':
    main()
