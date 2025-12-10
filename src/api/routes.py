from sqlalchemy import select
from src.database.models import IOLog

from flask import jsonify, make_response, request

from src.database import Database


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

    def list_io_events(self):
        """List IO events."""

        proc = request.args.get("proc", type=str)

        LocalSession = self.__db.new_session()
        session = LocalSession()
        query = select(IOLog)

        if proc is not None and len(proc) > 0:
            query = query.where(IOLog.proc.is_(proc))
        
        records = session.execute(query).scalars().all()

        return jsonify([r.to_dict() for r in records]), 200
