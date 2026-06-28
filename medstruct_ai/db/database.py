import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from medstruct_ai.core.schemas import ClinicalInsight, LabMetric, PatientRecord

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "medstruct.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(
                patient_name, notes, diagnoses, medications, clinical_insight_id UNINDEXED
            );

            CREATE TABLE IF NOT EXISTS patient_records (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name  TEXT    NOT NULL,
                last_name   TEXT    NOT NULL,
                dob         TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS clinical_insights (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id      INTEGER NOT NULL REFERENCES patient_records(id),
                visit_date      TEXT    NOT NULL,
                notes           TEXT,
                diagnoses       TEXT    DEFAULT '[]',
                medications     TEXT    DEFAULT '[]',
                overall_risk    TEXT    CHECK(overall_risk IN ('Low','Medium','High'))
            );

            CREATE TABLE IF NOT EXISTS lab_metrics (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                clinical_insight_id  INTEGER NOT NULL REFERENCES clinical_insights(id),
                name                 TEXT    NOT NULL,
                value                REAL    NOT NULL,
                unit                 TEXT    NOT NULL,
                is_abnormal          INTEGER NOT NULL DEFAULT 0
            );
        """)
        conn.commit()
    finally:
        conn.close()


def insert_patient_record(record: PatientRecord) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO patient_records (first_name, last_name, dob) VALUES (?, ?, ?)",
            (record.first_name, record.last_name, record.dob.isoformat()),
        )
        patient_id = cur.lastrowid
        for insight in record.insights:
            insert_clinical_insight(patient_id, insight, conn)
        conn.commit()
        return patient_id
    finally:
        conn.close()


def insert_clinical_insight(
    patient_id: int,
    insight: ClinicalInsight,
    conn: Optional[sqlite3.Connection] = None,
) -> int:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        cur = conn.execute(
            """INSERT INTO clinical_insights
               (patient_id, visit_date, notes, diagnoses, medications, overall_risk)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                patient_id,
                insight.visit_date.isoformat(),
                insight.notes,
                json.dumps(insight.diagnoses),
                json.dumps(insight.medications),
                insight.overall_risk,
            ),
        )
        insight_id = cur.lastrowid
        for metric in insight.lab_metrics:
            insert_lab_metric(insight_id, metric, conn)

        patient = conn.execute(
            "SELECT first_name, last_name FROM patient_records WHERE id = ?",
            (patient_id,),
        ).fetchone()
        if patient:
            patient_name = f"{patient['first_name']} {patient['last_name']}"
            conn.execute(
                """INSERT INTO search_fts (patient_name, notes, diagnoses, medications, clinical_insight_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    patient_name,
                    insight.notes or "",
                    ", ".join(insight.diagnoses),
                    ", ".join(insight.medications),
                    insight_id,
                ),
            )

        if own_conn:
            conn.commit()
        return insight_id
    finally:
        if own_conn:
            conn.close()


def insert_lab_metric(
    clinical_insight_id: int,
    metric: LabMetric,
    conn: Optional[sqlite3.Connection] = None,
) -> int:
    own_conn = False
    if conn is None:
        conn = get_connection()
        own_conn = True
    try:
        cur = conn.execute(
            """INSERT INTO lab_metrics
               (clinical_insight_id, name, value, unit, is_abnormal)
               VALUES (?, ?, ?, ?, ?)""",
            (clinical_insight_id, metric.name, metric.value, metric.unit, int(metric.is_abnormal)),
        )
        if own_conn:
            conn.commit()
        return cur.lastrowid
    finally:
        if own_conn:
            conn.close()


def get_all_patients() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, first_name, last_name, dob FROM patient_records ORDER BY last_name"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_metrics_for_charts(patient_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT lm.name, lm.value, lm.unit, lm.is_abnormal,
                      ci.visit_date, ci.overall_risk,
                      pr.first_name, pr.last_name
               FROM lab_metrics lm
               JOIN clinical_insights ci ON ci.id = lm.clinical_insight_id
               JOIN patient_records pr ON pr.id = ci.patient_id
               WHERE pr.id = ?
               ORDER BY ci.visit_date""",
            (patient_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_risk_summary() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT overall_risk, COUNT(*) as count
               FROM clinical_insights
               WHERE overall_risk IS NOT NULL
               GROUP BY overall_risk
               ORDER BY overall_risk"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_patient_record(patient_id: int) -> Optional[PatientRecord]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM patient_records WHERE id = ?", (patient_id,)
        ).fetchone()
        if row is None:
            return None
        insight_rows = conn.execute(
            "SELECT * FROM clinical_insights WHERE patient_id = ?", (patient_id,)
        ).fetchall()
        insights = []
        for ir in insight_rows:
            metric_rows = conn.execute(
                "SELECT * FROM lab_metrics WHERE clinical_insight_id = ?",
                (ir["id"],),
            ).fetchall()
            lab_metrics = [
                LabMetric(
                    name=m["name"],
                    value=m["value"],
                    unit=m["unit"],
                    is_abnormal=bool(m["is_abnormal"]),
                )
                for m in metric_rows
            ]
            insights.append(
                ClinicalInsight(
                    visit_date=date.fromisoformat(ir["visit_date"]),
                    notes=ir["notes"],
                    diagnoses=json.loads(ir["diagnoses"]),
                    medications=json.loads(ir["medications"]),
                    lab_metrics=lab_metrics,
                    overall_risk=ir["overall_risk"],
                )
            )
        return PatientRecord(
            first_name=row["first_name"],
            last_name=row["last_name"],
            dob=date.fromisoformat(row["dob"]),
            insights=insights,
        )
    finally:
        conn.close()
