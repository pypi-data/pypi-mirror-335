import palaestrai.store.database_model as dbm
import sqlalchemy.orm
from palaestrai.core import RuntimeConfig


def read_experiment_runs(experiment_id: int = 0, as_dict: bool = False):
    store_uri = RuntimeConfig().store_uri

    engine = sqlalchemy.create_engine(store_uri)
    session_maker = sqlalchemy.orm.sessionmaker()
    session_maker.configure(bind=engine)
    raw = []
    with session_maker() as session:
        if experiment_id > 0:
            runs = (
                session.query(dbm.ExperimentRun)
                .where(dbm.ExperimentRun.experiment_id == experiment_id)
                .order_by(dbm.ExperimentRun.id.asc())
            )
        else:
            runs = session.query(dbm.ExperimentRun).order_by(
                dbm.ExperimentRun.id.asc()
            )
        for run in runs.all():
            raw.append(run)

    if as_dict:
        results = {
            "run_id": [],
            "run_uid": [],
            "experiment_id": [],
        }
        for entry in raw:
            results["run_id"].append(entry.id)
            results["run_uid"].append(entry.uid)
            results["experiment_id"].append(entry.experiment_id)
    else:
        results = []
        for entry in raw:
            results.append(
                {
                    "run_id": entry.id,
                    "run_uid": entry.uid,
                    "experiment_id": entry.experiment_id,
                }
            )

    return results
