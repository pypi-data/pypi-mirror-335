import palaestrai.store.database_model as dbm
import sqlalchemy.orm
from palaestrai.core import RuntimeConfig


def read_experiments(as_dict: bool = False):
    store_uri = RuntimeConfig().store_uri

    engine = sqlalchemy.create_engine(store_uri)
    session_maker = sqlalchemy.orm.sessionmaker()
    session_maker.configure(bind=engine)
    raw = []
    with session_maker() as session:
        experiments = session.query(dbm.Experiment).order_by(
            dbm.Experiment.id.asc()
        )
        for exp in experiments.all():
            raw.append(exp)

    if as_dict:
        results = {"experiment_id": [], "experiment_name": []}
        for entry in raw:
            results["experiment_id"].append(entry.id)
            results["experiment_name"].append(entry.name)
    else:
        results = []
        for entry in raw:
            results.append(
                {"experiment_id": entry.id, "experiment_name": entry.name}
            )

    return results
