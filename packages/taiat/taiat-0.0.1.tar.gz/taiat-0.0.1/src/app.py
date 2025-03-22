from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from taiat.base import TaiatQuery
from taiat.db import PostgresDatabase
from taiat.service import TaiatService
from taiat.engine import TaiatEngine
from taiat.builder import TaiatBuilder
from taiat.generic_matcher import GenericMatcher


def initialize_services(app, db_connection_string: str, engine: TaiatEngine):
    engine = create_engine(db_connection_string)
    app.db = PostgresDatabase(session_maker=sessionmaker(bind=engine))
    app.service = TaiatService(
        engine=engine
    )

@app.route("/query", methods=["POST"])
def query(request: TaiatRequest):
    data = request["q"]
    query = TaiatQuery(**data)
    result = app.service.handle_query(query)
    return jsonify(result.model_dump())


if __name__ == "__main__":
    app = Flask(__name__)
    initialize_services(app, "postgresql://postgres:postgres@localhost:5432/postgres", engine)
    app.run(debug=True)
