import os
from shutil import which

import pytest

from smartsim.error.errors import LauncherError, SSConfigError
from smartsim.launcher.slurm.slurmStep import SlurmStep

if not which("srun"):
    pytestmark = pytest.mark.skip

cwd = os.path.dirname(os.path.abspath(__file__))
run_settings = {
    "nodes": 1,
    "ntasks": 1,
    "ntasks-per-node": 1,
    "out_file": cwd + "/out.txt",
    "err_file": cwd + "/err.txt",
    "cwd": cwd,
    "alloc": 111111,
    "executable": "a.out",
    "exe_args": "--input"
}

def test_build_cmd():
    """Test building the srun command"""
    step = SlurmStep("test-1111.0", run_settings, False)
    cmd = step.build_cmd()
    print(cmd)
    srun = which("srun")
    result = [srun,
              '--output', cwd + '/out.txt',
              '--error', cwd + '/err.txt',
              '--jobid', '111111', '--job-name', 'test-1111.0',
              '--nodes=1', '--ntasks=1', '--ntasks-per-node=1', 'a.out', '--input']
    assert(cmd == result)

def test_multi_prog():
    step = SlurmStep("test-1111.0", run_settings, True)
    cmd = step.build_cmd()
    print(cmd)
    srun = which("srun")
    result = [srun,
              '--output', cwd + '/out.txt',
              '--error', cwd + '/err.txt',
              '--jobid', '111111', '--job-name', 'test-1111.0',
              '--nodes=1', '--ntasks=1', '--ntasks-per-node=1',
              '--multi-prog', cwd + '/run_orc.conf'
                ]
    assert(cmd == result)
    assert(os.path.isfile(cwd + "/run_orc.conf"))
    os.remove(cwd + "/run_orc.conf")

run_settings_with_opts = {
    "nodes": 1,
    "n": 1,
    "out_file": cwd + "/out.txt",
    "err_file": cwd + "/err.txt",
    "cwd": cwd,
    "alloc": 111111,
    "executable": "a.out",
    "exe_args": "--input",
    "exclusive": None,    # --exclusive flag
    "qos": "interactive", # --qos flag
    "Q": None             # -Q
}

def test_build_cmd_with_opts():
    """Test building the srun command with extra options"""
    step = SlurmStep("test-1111.0", run_settings_with_opts, False)
    cmd = step.build_cmd()
    srun = which("srun")
    print(cmd)
    result = [srun, '--nodes', '1', '--ntasks', '1', '--ntasks-per-node', '1',
              '--output', cwd + '/out.txt',
              '--error', cwd + '/err.txt',
              '--jobid', '111111', '--job-name', 'test-1111.0',
              '--exclusive', '--qos=interactive', '-Q', 'a.out', '--input']
    result = [srun,
              '--output', cwd + '/out.txt',
              '--error', cwd + '/err.txt',
              '--jobid', '111111', '--job-name', 'test-1111.0',
              '--nodes=1', '-n', '1', '--exclusive', '--qos=interactive',
              '-Q', 'a.out', '--input']
    assert(cmd == result)

# ---------------------------------------------------------------
# error handling cases

run_settings_err_alloc = {
    "nodes": 1,
    "out_file": cwd + "/out.txt",
    "err_file": cwd + "/err.txt",
    "cwd": cwd,
    "executable": "a.out",
    "exe_args": "--input"
}
def test_no_alloc_given():
    """Test when the user fails to provide a step with an allocation"""
    with pytest.raises(SSConfigError):
        step = SlurmStep("test-1111.0", run_settings_err_alloc, False)


run_settings_err_exe = {
    "nodes": 1,
    "out_file": cwd + "/out.txt",
    "err_file": cwd + "/err.txt",
    "cwd": cwd,
    "exe_args": "--input",
    "alloc": 111111,
}
# this should actually be caught prior in entity intialization
# but we will test it anyway for code coverage
def test_no_executable():
    step = SlurmStep("test-1111.0", run_settings_err_exe, False)
    with pytest.raises(SSConfigError):
        cmd = step.build_cmd()
