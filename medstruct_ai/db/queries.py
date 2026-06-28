from medstruct_ai.db.database import get_connection


def search_patients(query: str) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT
                 fts.patient_name,
                 fts.notes,
                 fts.diagnoses,
                 fts.medications,
                 ci.id AS insight_id,
                 ci.visit_date,
                 ci.overall_risk,
                 pr.id AS patient_id,
                 pr.first_name,
                 pr.last_name,
                 pr.dob
               FROM search_fts fts
               JOIN clinical_insights ci ON ci.id = fts.clinical_insight_id
               JOIN patient_records pr ON pr.id = ci.patient_id
               WHERE search_fts MATCH ?
               ORDER BY rank
               LIMIT 50""",
            (query,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
