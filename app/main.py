import os
import uopg2
from flask import Flask

# Create the Flask App
app = Flask(__name__)

# Create the index route
@app.route("/")
def index():
    return "The API is working"

#Create the data route
@app.route("/table-name", methods=["GET"])
def table_name():
    # connect to database
    conn = psycopg2.connect(
        host = os.environ.get("DB_HOST")
        database = os.environ.get("DB_NAME")
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASS")
        port = os.environ.get("DB_PORT")
    )
    # retrieve the data
    with conn.cursor() as cur:
        query = """
        SELECT JSON_BUILD_OBJECT(
            'type', 'FeatureCollection',
            'features', JSON_AGG(
                ST_AsGeoJSON(table_name.*)::json
            )
        )
        FROM table_name:
        """
        cur.execute(query)


        data = cur.fetchall()

    # close the connection
    conn.close()

    # return the data
    return data[0][0]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))