import os
from shutil import which

import pytest

import smartsim.wlm as wlm
from smartsim.error.errors import LauncherError, SmartSimError, SSUnsupportedError

# alloc_specs can be specified by the user when testing, but it will
# require all WLM env variables to be populated. If alloc_specs is not
# defined, the tests in this file are skipped.

def test_get_hosts(alloc_specs):
    if not alloc_specs:
        pytest.skip("alloc_specs not defined")
    def verify_output(output):
        assert isinstance(output, list)
        assert all(isinstance(host, str) for host in output)
        if "host_list" in alloc_specs:
            assert output == alloc_specs["host_list"]

    if pytest.test_launcher == "slurm":
        if "SLURM_JOBID" in os.environ:
            verify_output(wlm.get_hosts())
        else:
            with pytest.raises(SmartSimError):
                wlm.get_hosts()

    elif pytest.test_launcher == "pbs":
        if "PBS_JOBID" in os.environ:
            verify_output(wlm.get_hosts())
        else:
            with pytest.raises(SmartSimError):
                wlm.get_hosts()

    else:
        with pytest.raises(SSUnsupportedError):
            wlm.get_hosts(launcher=pytest.test_launcher)


def test_get_queue(alloc_specs):
    if not alloc_specs:
        pytest.skip("alloc_specs not defined")
    def verify_output(output):
        assert isinstance(output, str)
        if "queue" in alloc_specs:
            assert output == alloc_specs["queue"]

    if pytest.test_launcher == "slurm":
        if "SLURM_JOBID" in os.environ:
            verify_output(wlm.get_queue())
        else:
            with pytest.raises(SmartSimError):
                wlm.get_queue()

    elif pytest.test_launcher == "pbs":
        if "PBS_JOBID" in os.environ:
            verify_output(wlm.get_queue())
        else:
            with pytest.raises(SmartSimError):
                wlm.get_queue()

    else:
        with pytest.raises(SSUnsupportedError):
            wlm.get_queue(launcher=pytest.test_launcher)


def test_get_tasks(alloc_specs):
    if not alloc_specs:
        pytest.skip("alloc_specs not defined")
    def verify_output(output):
        assert isinstance(output, int)
        if "num_tasks" in alloc_specs:
            assert output == alloc_specs["num_tasks"]

    if pytest.test_launcher == "slurm":
        if "SLURM_JOBID" in os.environ:
            verify_output(wlm.get_tasks())
        else:
            with pytest.raises(SmartSimError):
                wlm.get_tasks(launcher=pytest.test_launcher)

    elif pytest.test_launcher == "pbs":
        if "PBS_JOBID" in os.environ and which("qstat"):
            verify_output(wlm.get_tasks())
        elif "PBS_JOBID" in os.environ:
            with pytest.raises(LauncherError):
                wlm.get_tasks()
        else:
            with pytest.raises(SmartSimError):
                wlm.get_tasks()

    else:
        with pytest.raises(SSUnsupportedError):
            wlm.get_tasks(launcher=pytest.test_launcher)


def test_get_tasks_per_node(alloc_specs):
    if not alloc_specs:
        pytest.skip("alloc_specs not defined")
    def verify_output(output):
        assert isinstance(output, dict)
        assert all(
            isinstance(node, str) and isinstance(ntasks, int)
            for node, ntasks in output.items()
        )
        if "tasks_per_node" in alloc_specs:
            assert output == alloc_specs["tasks_per_node"]

    if pytest.test_launcher == "slurm":
        if "SLURM_JOBID" in os.environ:
            verify_output(wlm.get_tasks_per_node())
        else:
            with pytest.raises(SmartSimError):
                wlm.get_tasks_per_node()

    elif pytest.test_launcher == "pbs":
        if "PBS_JOBID" in os.environ and which("qstat"):
            verify_output(wlm.get_tasks_per_node())
        elif "PBS_JOBID" in os.environ:
            with pytest.raises(LauncherError):
                wlm.get_tasks_per_node()
        else:
            with pytest.raises(SmartSimError):
                wlm.get_tasks_per_node()

    else:
        with pytest.raises(SSUnsupportedError):
            wlm.get_tasks_per_node(launcher=pytest.test_launcher)
