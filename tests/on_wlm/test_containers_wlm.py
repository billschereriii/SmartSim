import pytest
from shutil import which

from smartsim import Experiment, status
from smartsim.entity import Ensemble
from smartsim.settings.containers import Singularity

"""Test SmartRedis container integration on a supercomputer with a WLM."""

# Check if singularity is available as command line tool
singularity_exists = which('singularity') is not None
containerURI = 'docker://alrigazzi/smartsim-testing:latest'

@pytest.mark.skipif(not singularity_exists, reason="Test needs singularity to run")
def test_singularity_wlm_smartredis(fileutils, wlmutils):
    """Run two processes, each process puts a tensor on
    the DB, then accesses the other process's tensor.
    Finally, the tensor is used to run a model.

    Note: This is a containerized port of test_smartredis.py for WLM system
    """

    launcher = wlmutils.get_test_launcher()
    print(launcher)
    if launcher not in ["pbs", "slurm"]:
        pytest.skip(
            f"Test only runs on systems with PBS or Slurm as WLM. Current launcher: {launcher}"
        )

    test_dir = fileutils.make_test_dir()
    exp = Experiment(
        "smartredis_ensemble_exchange", exp_path=test_dir, launcher=launcher
    )

    # create and start a database
    orc = exp.create_database()
    exp.generate()
    exp.start(orc, block=False)

    container = Singularity(containerURI)
    rs = exp.create_run_settings("python3", "producer.py --exchange", container=container)
    rs.set_tasks(1)
    params = {"mult": [1, -10]}
    ensemble = Ensemble(
        name="producer",
        params=params,
        run_settings=rs,
        perm_strat="step",
    )

    ensemble.register_incoming_entity(ensemble["producer_0"])
    ensemble.register_incoming_entity(ensemble["producer_1"])

    config = fileutils.get_test_conf_path("smartredis")
    ensemble.attach_generator_files(to_copy=[config])

    exp.generate(ensemble)

    # start the models
    exp.start(ensemble, summary=False)

    # get and confirm statuses
    statuses = exp.get_status(ensemble)
    if not all([stat == status.STATUS_COMPLETED for stat in statuses]):
        exp.stop(orc)
        assert False  # client ensemble failed

    # stop the orchestrator
    exp.stop(orc)

    print(exp.summary())

