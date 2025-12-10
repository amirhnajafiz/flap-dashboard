from flask import jsonify, make_response, request
from sqlalchemy import select

from src.database import Database
from src.database.models import IOLog


class Routes:
    """Routes methods will be used as api handler functinos."""

    def __init__(self, db: Database):
        """Routes constructor.

        :param db: Database module
        """
        self.__db = db

    def healthz(self):
        """Healthz return 200 on the /healthz endpoint."""
        return make_response("OK", 200)

    def get_files_count(self):
        """Get files count."""
        pass

    def get_files_bytes(self):
        """Get files bytes."""
        pass

    def get_files_duration(self):
        """Get files durations."""
        pass

    def list_procs(self):
        """List IO processes."""
        LocalSession = self.__db.new_session()
        session = LocalSession()

        query = select(IOLog.proc).distinct()
        records = session.execute(query).scalars().all()

        return jsonify(records), 200

    def list_io_events(self):
        """List IO events."""

        proc = request.args.get("proc", type=str)
        hide_unknown = request.args.get("hunk", type=str)

        LocalSession = self.__db.new_session()
        session = LocalSession()

        query = select(IOLog)

        if proc is not None and len(proc) > 0:
            query = query.where(IOLog.proc.is_(proc))
        if hide_unknown == "true":
            query = query.where(IOLog.fname.is_not("unknown"))

        records = session.execute(query).scalars().all()

        return jsonify([r.to_dict() for r in records]), 200
