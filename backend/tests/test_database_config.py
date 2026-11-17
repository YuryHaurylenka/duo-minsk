from app.database import DATABASE_CONNECT_ARGS


def test_psycopg_prepared_statements_are_disabled_for_transaction_pooler():
    assert DATABASE_CONNECT_ARGS["prepare_threshold"] is None
