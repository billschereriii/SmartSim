import pytest

from smartsim.error import SSUnsupportedError
from smartsim.settings import SbatchSettings, SrunSettings

# ------ Srun ------------------------------------------------


def test_srun_settings():
    settings = SrunSettings("python")
    settings.set_nodes(5)
    settings.set_cpus_per_task(2)
    settings.set_tasks(100)
    settings.set_tasks_per_node(20)
    formatted = settings.format_run_args()
    result = ["--nodes=5", "--cpus-per-task=2", "--ntasks=100", "--ntasks-per-node=20"]
    assert formatted == result


def test_srun_args():
    """Test the possible user overrides through run_args"""
    run_args = {
        "account": "A3123",
        "exclusive": None,
        "C": "P100",  # test single letter variables
        "nodes": 10,
        "ntasks": 100,
    }
    settings = SrunSettings("python", run_args=run_args)
    formatted = settings.format_run_args()
    result = [
        "--account=A3123",
        "--exclusive",
        "-C",
        "P100",
        "--nodes=10",
        "--ntasks=100",
    ]
    assert formatted == result


def test_update_env():
    env_vars = {"OMP_NUM_THREADS": 20, "LOGGING": "verbose"}
    settings = SrunSettings("python", env_vars=env_vars)
    settings.update_env({"OMP_NUM_THREADS": 10})
    assert settings.env_vars["OMP_NUM_THREADS"] == 10


def test_catch_colo_mpmd():
    srun = SrunSettings("python")
    srun.colocated_db_settings = {"port": 6379, "cpus": 1}
    srun_2 = SrunSettings("python")

    # should catch the user trying to make rs mpmd that already are colocated
    with pytest.raises(SSUnsupportedError):
        srun.make_mpmd(srun_2)


def test_format_env_vars():
    rs = SrunSettings(
        "python",
        env_vars={
            "OMP_NUM_THREADS": 20,
            "LOGGING": "verbose",
            "SSKEYIN": "name_0,name_1",
        },
    )
    formatted = rs.format_env_vars()
    assert "OMP_NUM_THREADS=20" in formatted
    assert "LOGGING=verbose" in formatted
    assert all("SSKEYIN" not in x for x in formatted)


def test_format_comma_sep_env_vars():
    env_vars = {"OMP_NUM_THREADS": 20, "LOGGING": "verbose", "SSKEYIN": "name_0,name_1"}
    settings = SrunSettings("python", env_vars=env_vars)
    formatted, comma_separated_formatted = settings.format_comma_sep_env_vars()
    assert "OMP_NUM_THREADS" in formatted
    assert "LOGGING" in formatted
    assert "SSKEYIN" in formatted
    assert "SSKEYIN=name_0,name_1" in comma_separated_formatted


@pytest.mark.parametrize("reserved_arg", ["chdir", "D"])
def test_no_set_reserved_args(reserved_arg):
    srun = SrunSettings("python")
    srun.set(reserved_arg)
    assert reserved_arg not in srun.run_args


def test_set_tasks():
    rs = SrunSettings("python")
    rs.set_tasks(6)
    assert rs.run_args["ntasks"] == 6

    with pytest.raises(ValueError):
        rs.set_tasks("not an int")


def test_set_tasks_per_node():
    rs = SrunSettings("python")
    rs.set_tasks_per_node(6)
    assert rs.run_args["ntasks-per-node"] == 6

    with pytest.raises(ValueError):
        rs.set_tasks_per_node("not an int")


def test_set_cpus_per_task():
    rs = SrunSettings("python")
    rs.set_cpus_per_task(6)
    assert rs.run_args["cpus-per-task"] == 6

    with pytest.raises(ValueError):
        rs.set_cpus_per_task("not an int")


def test_set_hostlist():
    rs = SrunSettings("python")
    rs.set_hostlist(["host_A", "host_B"])
    assert rs.run_args["nodelist"] == "host_A,host_B"

    rs.set_hostlist("host_A")
    assert rs.run_args["nodelist"] == "host_A"

    with pytest.raises(TypeError):
        rs.set_hostlist([5])


def test_set_hostlist_from_file():
    rs = SrunSettings("python")
    rs.set_hostlist_from_file("./path/to/hostfile")
    assert rs.run_args["nodefile"] == "./path/to/hostfile"

    rs.set_hostlist_from_file("~/other/file")
    assert rs.run_args["nodefile"] == "~/other/file"


def test_set_cpu_bindings():
    rs = SrunSettings("python")
    rs.set_cpu_bindings([1, 2, 3, 4])
    assert rs.run_args["cpu_bind"] == "map_cpu:1,2,3,4"

    rs.set_cpu_bindings(2)
    assert rs.run_args["cpu_bind"] == "map_cpu:2"

    with pytest.raises(ValueError):
        rs.set_cpu_bindings(["not_an_int"])


def test_set_memory_per_node():
    rs = SrunSettings("python")
    rs.set_memory_per_node(8000)
    assert rs.run_args["mem"] == "8000M"

    with pytest.raises(ValueError):
        rs.set_memory_per_node("not_an_int")


def test_set_verbose():
    rs = SrunSettings("python")
    rs.set_verbose_launch(True)
    assert "verbose" in rs.run_args

    rs.set_verbose_launch(False)
    assert "verbose" not in rs.run_args

    # Ensure not error on repeat calls
    rs.set_verbose_launch(False)


def test_quiet_launch():
    rs = SrunSettings("python")
    rs.set_quiet_launch(True)
    assert "quiet" in rs.run_args

    rs.set_quiet_launch(False)
    assert "quiet" not in rs.run_args

    # Ensure not error on repeat calls
    rs.set_quiet_launch(False)


def test_set_broadcast():
    rs = SrunSettings("python")
    rs.set_broadcast("/tmp/some/path")
    assert rs.run_args["bcast"] == "/tmp/some/path"


def test_set_time():
    rs = SrunSettings("python")
    rs.set_time(seconds=72)
    assert rs.run_args["time"] == "00:01:12"

    rs.set_time(hours=1, minutes=31, seconds=1845)
    assert rs.run_args["time"] == "02:01:45"

    rs.set_time(hours=11)
    assert rs.run_args["time"] == "11:00:00"

    rs.set_time(seconds=0)
    assert rs.run_args["time"] == "00:00:00"

    with pytest.raises(ValueError):
        rs.set_time("not an int")


# ---- Sbatch ---------------------------------------------------


def test_sbatch_settings():
    sbatch = SbatchSettings(nodes=1, time="10:00:00", account="A3123")
    formatted = sbatch.format_batch_args()
    result = ["--nodes=1", "--time=10:00:00", "--account=A3123"]
    assert formatted == result


def test_sbatch_manual():
    sbatch = SbatchSettings()
    sbatch.set_nodes(5)
    sbatch.set_account("A3531")
    sbatch.set_walltime("10:00:00")
    formatted = sbatch.format_batch_args()
    result = ["--nodes=5", "--account=A3531", "--time=10:00:00"]
    assert formatted == result


def test_change_batch_cmd():
    sbatch = SbatchSettings()
    sbatch.set_batch_command("qsub")
    assert sbatch._batch_cmd == "qsub"
