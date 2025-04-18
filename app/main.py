import os
import psycopg2
from flask import Flask

# Create the Flask App
app = Flask(__name__)

# Create the index route
@app.route("/")
def index():
    return "The API is working"

# Create General DB to GeoJSON Function
def database_to_geojson(table_name):
    # connect to database
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database = os.environ.get("DB_NAME"),
        user = os.environ.get("DB_USER"),
        password = os.environ.get("DB_PASS"),
        port = os.environ.get("DB_PORT")
    )

    # retrieve the data
    with conn.cursor() as cur:
        query = f"""
            SELECT JSON_BUILD_OBJECT(
                'type', 'FeatureCollection',
                'features', JSON_AGG(
                    ST_AsGeoJSON({table_name}.*)::json
                )
            )
            FROM {table_name};
            """
        cur.execute(query)

        data = cur.fetchall()
    # close the connection
    conn.close()

    # return the data
    return data[0][0]

#Create the data route
@app.route("/dem", methods=["GET"])
def dem_points():
    # Call our general function
    dem = database_to_geojson("galayer_dem")

    return dem

#Create the data route
@app.route("/dem_error", methods=["GET"])
def dem_error():
    # Call our general function
    dem = database_to_geojson("galayer_dem")

    return dem

# Create the data route
@app.route("/cdd", methods=["GET"])
def cdd_data():
    # Call our general function
    cdd_data = database_to_geojson("galayer_cdd")

    return cdd_data

# Build JSON for cdd error
@app.route("/cdd_error", methods=["GET"])
def cdd_error():
    # Connect to the database
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        port=os.environ.get("DB_PORT")
    )

    cursor = conn.cursor()

    # Query only the 'Standard Error' column and geometry
    query = """
        SELECT "Standard Error", ST_AsGeoJSON(geom) 
        FROM galayer_cdd
        WHERE "Standard Error" IS NOT NULL;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Build GeoJSON features
    features = []
    for value, geom_json in rows:
        features.append({
            "type": "Feature",
            "geometry": json.loads(geom_json),
            "properties": {
                "Standard Error": value
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    cursor.close()
    conn.close()

    return jsonify(geojson)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))