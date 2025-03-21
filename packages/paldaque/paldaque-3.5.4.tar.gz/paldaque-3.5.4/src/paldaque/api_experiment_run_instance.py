import palaestrai.store.database_model as dbm
import sqlalchemy.orm
from palaestrai.core import RuntimeConfig


def read_experiment_run_instances(
    experiment_id: int = 0, experiment_run_id: int = 0, as_dict: bool = False
):
    if experiment_run_id > 0:
        level = 1
    elif experiment_id > 0:
        level = 2
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
                session.query(dbm.ExperimentRunInstance, dbm.ExperimentRun)
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .order_by(dbm.ExperimentRunInstance.id.asc())
            )
        elif level == 1:
            entries = (
                session.query(dbm.ExperimentRunInstance, dbm.ExperimentRun)
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(dbm.ExperimentRun.id == experiment_run_id)
                .order_by(dbm.ExperimentRunInstance.id.asc())
            )
        else:
            entries = (
                session.query(dbm.ExperimentRunInstance, dbm.ExperimentRun)
                .join(
                    dbm.ExperimentRun,
                    dbm.ExperimentRunInstance.experiment_run_id
                    == dbm.ExperimentRun.id,
                )
                .where(dbm.ExperimentRun.experiment_id == experiment_id)
                .order_by(dbm.ExperimentRunInstance.id.asc())
            )
        # if experiment_id > 0:
        #     runs = (
        #         session.query(dbm.ExperimentRunInstance)
        #         .where(dbm.ExperimentRun.experiment_id == experiment_id)
        #         .order_by(dbm.ExperimentRun.id.asc())
        #     )
        # else:
        #     runs = session.query(dbm.ExperimentRun).order_by(
        #         dbm.ExperimentRun.id.asc()
        #     )
        for entry in entries.all():
            raw.append(entry)

    if as_dict:
        results = {
            "instance_id": [],
            "instance_uid": [],
            "run_id": [],
            "experiment_id": [],
        }
        for entry in raw:
            results["instance_id"].append(entry.ExperimentRunInstance.id)
            results["instance_uid"].append(entry.ExperimentRunInstance.uid)
            results["run_id"].append(entry.ExperimentRun.id)
            results["experiment_id"].append(entry.ExperimentRun.experiment_id)
    else:
        results = []
        for entry in raw:
            results.append(
                {
                    "instance_id": entry.ExperimentRunInstance.id,
                    "instance_uid": entry.ExperimentRunInstance.uid,
                    "run_id": entry.ExperimentRun.id,
                    "experiment_id": entry.ExperimentRun.experiment_id,
                }
            )

    return results
