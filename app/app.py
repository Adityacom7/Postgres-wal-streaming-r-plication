from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_CONFIG_MASTER = {
    'host': os.getenv('DB_MASTER_HOST', 'postgres-master'),
    'port': os.getenv('DB_MASTER_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'scandb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

DB_CONFIG_SLAVE = {
    'host': os.getenv('DB_SLAVE_HOST', 'postgres-slave'),
    'port': os.getenv('DB_SLAVE_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'scandb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection(use_slave=False):
    """Get database connection - master for writes, slave for reads"""
    config = DB_CONFIG_SLAVE if use_slave else DB_CONFIG_MASTER
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        # Fallback to master if slave is unavailable
        if use_slave:
            print(f"Slave connection failed, falling back to master: {e}")
            return psycopg2.connect(**DB_CONFIG_MASTER)
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/db-status', methods=['GET'])
def db_status():
    """Check database and replication status"""
    try:
        # Check master connection
        conn_master = get_db_connection(use_slave=False)
        cur_master = conn_master.cursor(cursor_factory=RealDictCursor)
        cur_master.execute("SELECT pg_is_in_recovery(), version();")
        master_info = cur_master.fetchone()
        
        # Check replication status
        cur_master.execute("SELECT * FROM pg_stat_replication;")
        replication_status = cur_master.fetchall()
        
        cur_master.close()
        conn_master.close()
        
        # Check slave connection
        slave_status = "unavailable"
        slave_info = None
        try:
            conn_slave = get_db_connection(use_slave=True)
            cur_slave = conn_slave.cursor(cursor_factory=RealDictCursor)
            cur_slave.execute("SELECT pg_is_in_recovery(), pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();")
            slave_info = cur_slave.fetchone()
            slave_status = "available"
            cur_slave.close()
            conn_slave.close()
        except Exception as e:
            slave_status = f"error: {str(e)}"
        
        return jsonify({
            'master': {
                'status': 'available',
                'is_in_recovery': master_info['pg_is_in_recovery'],
                'version': master_info['version']
            },
            'slave': {
                'status': slave_status,
                'info': slave_info
            },
            'replication': replication_status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def submit_scan():
    """Submit scan data - writes to master"""
    try:
        data = request.get_json()
        
        if not data or 'client_id' not in data or 'scan_data' not in data:
            return jsonify({'error': 'Invalid data. Required fields: client_id, scan_data'}), 400
        
        client_id = data['client_id']
        scan_data = json.dumps(data['scan_data'])
        
        conn = get_db_connection(use_slave=False)
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO scan_results (client_id, scan_data) VALUES (%s, %s) RETURNING id, created_at;",
            (client_id, scan_data)
        )
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': result[0],
            'created_at': result[1].isoformat(),
            'message': 'Scan data submitted successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scans', methods=['GET'])
def get_scans():
    """Retrieve all scans - reads from slave when available"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        conn = get_db_connection(use_slave=True)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT id, client_id, scan_data, created_at FROM scan_results ORDER BY created_at DESC LIMIT %s OFFSET %s;",
            (limit, offset)
        )
        
        scans = cur.fetchall()
        
        # Get total count
        cur.execute("SELECT COUNT(*) FROM scan_results;")
        total_count = cur.fetchone()['count']
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'scans': scans
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scans/<int:scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Retrieve a specific scan by ID"""
    try:
        conn = get_db_connection(use_slave=True)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT id, client_id, scan_data, created_at FROM scan_results WHERE id = %s;",
            (scan_id,)
        )
        
        scan = cur.fetchone()
        cur.close()
        conn.close()
        
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        return jsonify({
            'success': True,
            'scan': scan
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
