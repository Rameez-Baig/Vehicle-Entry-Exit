from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Rameez123$',
    'database': 'CAR1'
}

# Connect to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

@app.route('/vehicle_entry_exit', methods=['GET'])
def get_vehicle_entry_exit():
    try:
        vehicle_id = request.args.get('vehicle_id')
        start_datetime = request.args.get('start_datetime')
        end_datetime = request.args.get('end_datetime')

        # Construct the SQL query
        query = "SELECT ENTRY_TIME, EXIT_TIME, VEHICLE_ID, GATE_NO FROM GATE WHERE 1=1"
        if vehicle_id:
            query += f" AND VEHICLE_ID = '{vehicle_id}'"
        if start_datetime and end_datetime:
            query += f" AND ENTRY_TIME BETWEEN '{start_datetime}' AND '{end_datetime}'"

        # Execute the query
        cursor.execute(query)
        records = cursor.fetchall()

        # Convert records to JSON format
        result = []
        for record in records:
            entry_time, exit_time, vehicle_id, gate_no = record
            result.append({
                'entry_time': entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                'exit_time': exit_time.strftime("%Y-%m-%d %H:%M:%S") if exit_time else 'NULL',
                'vehicle_id': vehicle_id,
                'gate_no': gate_no
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/search_by_vehicle_id', methods=['POST'])
def search_by_vehicle_id():
    try:
        data = request.get_json()
        vehicle_id = data.get('vehicle_id')

        # Construct the SQL query
        query = f"SELECT ENTRY_TIME, EXIT_TIME, VEHICLE_ID, GATE_NO FROM GATE WHERE VEHICLE_ID = '{vehicle_id}'"

        # Execute the query
        cursor.execute(query)
        records = cursor.fetchall()

        # Convert records to JSON format
        result = []
        for record in records:
            entry_time, exit_time, vehicle_id, gate_no = record
            result.append({
                'entry_time': entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                'exit_time': exit_time.strftime("%Y-%m-%d %H:%M:%S") if exit_time else 'NULL',
                'vehicle_id': vehicle_id,
                'gate_no': gate_no
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_by_datetime_range', methods=['POST'])
def search_by_datetime_range():
    try:
        data = request.get_json()
        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')

        # Construct the SQL query to filter based on ENTRY_TIME and EXIT_TIME
        query = f"""
            SELECT ENTRY_TIME, EXIT_TIME, VEHICLE_ID, GATE_NO 
            FROM GATE 
            WHERE ENTRY_TIME >= '{start_datetime}' 
            AND EXIT_TIME <= '{end_datetime}' 
            AND EXIT_TIME IS NOT NULL
        """

        # Execute the query
        cursor.execute(query)
        records = cursor.fetchall()

        # Convert records to JSON format
        result = []
        for record in records:
            entry_time, exit_time, vehicle_id, gate_no = record
            result.append({
                'entry_time': entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                'exit_time': exit_time.strftime("%Y-%m-%d %H:%M:%S"),
                'vehicle_id': vehicle_id,
                'gate_no': gate_no
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/defaulters', methods=['GET'])
def get_defaulters():
    try:
        # Construct the SQL query to find vehicles that have not exited
        query = "SELECT ENTRY_TIME, VEHICLE_ID, GATE_NO FROM GATE WHERE EXIT_TIME IS NULL"

        # Execute the query
        cursor.execute(query)
        records = cursor.fetchall()

        # Convert records to JSON format
        result = []
        for record in records:
            entry_time, vehicle_id, gate_no = record
            result.append({
                'entry_time': entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                'exit_time': 'NOT EXITED',
                'vehicle_id': vehicle_id,
                'gate_no': gate_no
# The `            ` in the code snippet you provided is used for indentation. In Python, indentation
# is crucial for defining the structure of the code. It helps in visually organizing blocks of code
# and determining the scope of statements within loops, conditions, functions, and classes.
            })

        # Count the number of defaulters
        defaulters_count = len(records)

        response = {
            'defaulters': result,
            'defaulters_count': defaulters_count
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/vehicle_stats', methods=['POST'])
def get_vehicle_stats():
    try:
        data = request.get_json()
        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')

        # Initialize result dictionary to store stats gate-wise
        gate_stats = {}

        # Define gate numbers for which you want statistics
        gate_numbers = [1, 4, 9]

        # Query statistics for each gate
        for gate_no in gate_numbers:
            # Construct SQL queries for each gate
            query_entered = f"SELECT COUNT(*) FROM GATE WHERE GATE_NO = {gate_no} AND ENTRY_TIME BETWEEN '{start_datetime}' AND '{end_datetime}'"
            query_exited = f"SELECT COUNT(*) FROM GATE WHERE GATE_NO = {gate_no} AND EXIT_TIME BETWEEN '{start_datetime}' AND '{end_datetime}'"

            # Execute the queries
            cursor.execute(query_entered)
            vehicles_entered = cursor.fetchone()[0]

            cursor.execute(query_exited)
            vehicles_exited = cursor.fetchone()[0]

            # Calculate the number of vehicles not exited for this gate
            vehicles_not_exited = vehicles_entered - vehicles_exited

            # Calculate the percentage of vehicles not exited for this gate
            if vehicles_entered == 0:
                percentage_not_exited = 0
            else:
                percentage_not_exited = (vehicles_not_exited / vehicles_entered) * 100

            # Round percentage_not_exited to 2 decimal places
            percentage_not_exited = round(percentage_not_exited, 2)

            # Store stats for this gate in the gate_stats dictionary
            gate_stats[f"Gate {gate_no}"] = {
                'vehicles_entered': vehicles_entered,
                'vehicles_exited': vehicles_exited,
                'vehicles_not_exited': vehicles_not_exited,
                'percentage_not_exited': percentage_not_exited
            }

        return jsonify(gate_stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '_main_':
    app.run(debug=True, port=5000)