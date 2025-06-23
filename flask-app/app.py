from flask import Flask, jsonify
from cassandra.cluster import Cluster

app = Flask(__name__)

@app.route("/fraud")
def get_frauds():
    cluster = Cluster(["cassandra"])
    session = cluster.connect("fraud")
    rows = session.execute("SELECT * FROM alerts")
    result = [dict(row._asdict()) for row in rows]
    cluster.shutdown()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
