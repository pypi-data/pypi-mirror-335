import palaestrai.store.database_model as dbm
import sqlalchemy.orm
from palaestrai.core import RuntimeConfig


def read_experiment_run_phases(
    experiment_id: int = 0,
    experiment_run_id: int = 0,
    experiment_run_instance_id: int = 0,
    as_dict: bool = False,
):
    if experiment_run_instance_id > 0:
        level = 1
    elif experiment_run_id > 0:
        level = 2
    elif experiment_id > 0:
        level = 3
    else:
        level = 0

    store_uri = RuntimeConfig().store_uri

    engine = sqlalchemy.create_engine(store_uri)
    session_maker = sqlalchemy.orm.sessionmaker()
    session_maker.configure(bind=engine)
    raw = []
    with session_maker() as session:
        if level == 0:
            entries = (
                session.query(
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunInstance.id
                    == dbm.ExperimentRunPhase.experiment_run_instance_id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
            )
        elif level == 1:
            entries = (
                session.query(
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunInstance.id
                    == dbm.ExperimentRunPhase.experiment_run_instance_id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(
                    dbm.ExperimentRunInstance.id == experiment_run_instance_id
                )
            )
        elif level == 2:
            entries = (
                session.query(
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunInstance.id
                    == dbm.ExperimentRunPhase.experiment_run_instance_id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(dbm.ExperimentRun.id == experiment_run_id)
            )
        elif level == 3:
            entries = (
                session.query(
                    dbm.ExperimentRunPhase,
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRun,
                )
                .join(
                    dbm.ExperimentRunInstance,
                    dbm.ExperimentRunInstance.id
                    == dbm.ExperimentRunPhase.experiment_run_instance_id,
                )
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(dbm.ExperimentRun.experiment_id == experiment_id)
            )

        for entry in entries.all():
            raw.append(entry)

    if as_dict:
        results = {
            "phase_id": [],
            "phase_uid": [],
            "phase_mode": [],
            "phase_number": [],
            "instance_id": [],
            "run_id": [],
            "experiment_id": [],
        }
        for entry in raw:
            results["phase_id"].append(entry.ExperimentRunPhase.id)
            results["phase_uid"].append(entry.ExperimentRunPhase.uid)
            results["phase_mode"].append(entry.ExperimentRunPhase.mode)
            results["phase_number"].append(entry.ExperimentRunPhase.number)
            results["instance_id"].append(entry.ExperimentRunInstance.id)
            results["run_id"].append(entry.ExperimentRun.id)
            results["experiment_id"].append(entry.ExperimentRun.experiment_id)
    else:
        results = []
        for entry in raw:
            results.append(
                {
                    "phase_id": entry.ExperimentRunPhase.id,
                    "phase_uid": entry.ExperimentRunPhase.uid,
                    "phase_mode": entry.ExperimentRunPhase.mode,
                    "phase_number": entry.ExperimentRunPhase.number,
                    "instance_id": entry.ExperimentRunInstance.id,
                    "run_id": entry.ExperimentRun.id,
                    "experiment_id": entry.ExperimentRun.experiment_id,
                }
            )

    return results
