from flask import jsonify, make_response, request
from sqlalchemy import asc, desc, func, select

from src.database import Database
from src.database.models import IOLog

PAGE_SIZE = 20


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
        """Get files count grouped by file, with pagination."""
        proc = request.args.get("proc", type=str)
        page = request.args.get("page", default=1, type=int)
        desc_value = request.args.get("desc", default="false", type=str).lower()
        hide_unknown = request.args.get("hunk", type=str)
        remove_stds = request.args.get("rmstd", type=str)

        session = self.__db.new_session()()

        base_query = (
            select(IOLog.fname, func.count().label("value"))
            .where(IOLog.proc.is_(proc))
            .where(IOLog.event_name.is_not("close"))
            .group_by(IOLog.fname)
        )
        base_query = (
            base_query.where(IOLog.fname.is_not("unknown"))
            if hide_unknown and hide_unknown == "true"
            else base_query
        )
        base_query = (
            base_query.where(IOLog.fd.not_in([0, 1, 2]))
            if remove_stds and remove_stds == "true"
            else base_query
        )

        count_subq = base_query.subquery()
        total = session.query(func.count()).select_from(count_subq).scalar()

        ordering = desc("value") if desc_value == "true" else asc("value")

        page_size = PAGE_SIZE
        offset = (page - 1) * page_size

        query = base_query.order_by(ordering).limit(page_size).offset(offset)
        rows = session.execute(query).all()

        total_pages = (total + page_size - 1) // page_size

        response = {
            "data": [dict(r._asdict()) for r in rows],
            "page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "total": total,
            "total_pages": total_pages,
            "page_size": page_size,
            "unit": "Hits"
        }

        return jsonify(response)

    def get_files_bytes(self):
        """Get files bytes."""
        proc = request.args.get("proc", type=str)
        page = request.args.get("page", default=1, type=int)
        desc_value = request.args.get("desc", default="false", type=str).lower()
        hide_unknown = request.args.get("hunk", type=str)
        remove_stds = request.args.get("rmstd", type=str)

        session = self.__db.new_session()()

        base_query = (
            select(IOLog.fname, func.sum(IOLog.countbytes).label("value"))
            .where(IOLog.proc.is_(proc))
            .where(IOLog.event_name.is_not("close"))
            .group_by(IOLog.fname)
        )
        base_query = (
            base_query.where(IOLog.fname.is_not("unknown"))
            if hide_unknown and hide_unknown == "true"
            else base_query
        )
        base_query = (
            base_query.where(IOLog.fd.not_in([0, 1, 2]))
            if remove_stds and remove_stds == "true"
            else base_query
        )

        count_subq = base_query.subquery()
        total = session.query(func.count()).select_from(count_subq).scalar()

        ordering = desc("value") if desc_value == "true" else asc("value")

        page_size = PAGE_SIZE
        offset = (page - 1) * page_size

        query = base_query.order_by(ordering).limit(page_size).offset(offset)
        rows = session.execute(query).all()

        total_pages = (total + page_size - 1) // page_size

        response = {
            "data": [dict(r._asdict()) for r in rows],
            "page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "total": total,
            "total_pages": total_pages,
            "page_size": page_size,
            "unit": "Bytes"
        }

        return jsonify(response)

    def get_files_duration(self):
        """Get files durations."""
        proc = request.args.get("proc", type=str)
        page = request.args.get("page", default=1, type=int)
        desc_value = request.args.get("desc", default="false", type=str).lower()
        hide_unknown = request.args.get("hunk", type=str)
        remove_stds = request.args.get("rmstd", type=str)

        session = self.__db.new_session()()

        base_query = (
            select(
                IOLog.fname,
                func.sum(IOLog.latency).label("value"),
            )
            .where(IOLog.proc.is_(proc))
            .where(IOLog.event_name.is_not("close"))
            .group_by(IOLog.fname)
        )
        base_query = (
            base_query.where(IOLog.fname.is_not("unknown"))
            if hide_unknown and hide_unknown == "true"
            else base_query
        )
        base_query = (
            base_query.where(IOLog.fd.not_in([0, 1, 2]))
            if remove_stds and remove_stds == "true"
            else base_query
        )

        count_subq = base_query.subquery()
        total = session.query(func.count()).select_from(count_subq).scalar()

        ordering = (
            desc("value") if desc_value == "true" else asc("value")
        )

        page_size = PAGE_SIZE
        offset = (page - 1) * page_size

        query = base_query.order_by(ordering).limit(page_size).offset(offset)
        rows = session.execute(query).all()

        total_pages = (total + page_size - 1) // page_size

        response = {
            "data": [dict(r._asdict()) for r in rows],
            "page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "total": total,
            "total_pages": total_pages,
            "page_size": page_size,
            "unit": "Latency (ns)"
        }

        return jsonify(response)

    def list_procs(self):
        """List IO processes."""
        session = self.__db.new_session()()

        query = select(IOLog.proc).distinct()
        records = session.execute(query).scalars().all()

        return jsonify(records), 200

    def list_io_events(self):
        """List IO events."""

        proc = request.args.get("proc", type=str)
        hide_unknown = request.args.get("hunk", type=str)
        remove_stds = request.args.get("rmstd", type=str)
        fname = request.args.get("fname", type=str)

        session = self.__db.new_session()()

        query = select(IOLog)

        query = query.where(IOLog.proc.is_(proc)) if proc and len(proc) > 0 else query
        query = (
            query.where(IOLog.fname.is_not("unknown"))
            if hide_unknown and hide_unknown == "true"
            else query
        )
        query = (
            query.where(IOLog.fd.not_in([0, 1, 2]))
            if remove_stds and remove_stds == "true"
            else query
        )
        query = (
            query.where(IOLog.fname.is_(fname)) if fname and len(fname) > 0 else query
        )

        records = session.execute(query).scalars().all()

        return jsonify([r.to_dict() for r in records]), 200
