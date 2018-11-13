
TABLE_OCCURRENCES = "OccurrencesV3"
TABLE_RANDOM = "Random"
TABLE_PROTECTED_AREAS = "ProtectedAreas"

def CompileOccurrenceSQLQuery(table, dates=None):

    if table not in [TABLE_OCCURRENCES, TABLE_RANDOM, TABLE_PROTECTED_AREAS]:
        raise ValueError("Invalid table name")

    if table == TABLE_PROTECTED_AREAS and dates is None:
        raise ValueError("ProtectedAreas requires at least one date")

    s = "SELECT * FROM Floracast.%s" % table

    if table == TABLE_OCCURRENCES:
        s = (
            "SELECT * FROM ("
                "SELECT *, ROW_NUMBER() OVER("
                  "PARTITION BY source_key, source_id ORDER BY created_at DESC"
                ") AS row_number "
                "FROM Floracast.{table} "
            ") WHERE row_number = 1 "
        ).format(table=table)

        s = (
            "SELECT * FROM ("
              "SELECT *, COUNT(*) OVER(PARTITION BY name) AS name_count "
              "FROM ({s})"
            ")"
            " WHERE name_count > 200"
        ).format(s=s)

    if dates is not None:
        s = (
            "SELECT * "
            "FROM ({s}) "
            "CROSS JOIN UNNEST ([{dates}]) as observed_at"
        ).format(
            s=s,
            dates=", ".join(["TIMESTAMP(%s)" % x for x in dates])
        )

    return (
        "with occurrences as ({s}) "
        "SELECT source_id, source_key, observed_at, cell_id, name "
        "FROM occurrences "
        "CROSS JOIN UNNEST (cell_ids) as cell_id "
        "LIMIT 500"
    ).format(s=s)

if __name__ == "__main__":
    print(CompileOccurrenceSQLQuery(TABLE_OCCURRENCES))