from django.db import connection


def make_json_postgres(query, params):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            results = []

    return results
