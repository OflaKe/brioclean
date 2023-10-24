from flask import Flask, render_template
from flask_socketio import SocketIO
import serial
import threading
import time
import sqlite3
import os
import re


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')
ser = None
stop_reading = threading.Event()

database = 'data.db'
table_name = 'measurements'
num_measurements = 10
paused_reading = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hold', methods=['POST'])
def hold():
    global paused_reading
    paused_reading = not paused_reading  # Toggle the state of paused_reading
    return '', 200


@socketio.on('connect')
def test_connect():
    global ser
    print('Client connected')
    try:
        ser = serial.Serial('COM3', 9600, timeout=1)
        stop_reading.clear()  # Reset the event flag
        threading.Thread(target=read_serial).start()
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

def read_serial():
    global ser, stop_reading
    while not stop_reading.is_set():
        try:
            if ser:
                raw_data = ser.readline().decode().strip()
                if raw_data != '':
                    if not paused_reading:
                        pattern = r"[-+]?\d+\.\d{1,2}"
                        matches = re.findall(pattern, raw_data)
                        if matches:
                            values = [float(match) * 10 for match in matches if float(match) != 0.0]
                            rounded_values = [round(value, 1) for value in values]
                            print("Measured values:")
                            for value in rounded_values:
                                print(value)
                                save_measurements([value])  # Save each value to the database
                                socketio.emit('send_data', value)  # Emit rounded values to clients
                        else:
                            print("No numeric values found")
        except Exception as e:
            print(f"Error reading serial port: {e}")


def save_measurements(data):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (measurement INTEGER, value REAL)")
    conn.commit()
    
    last_measurement = c.execute(f"SELECT MAX(measurement) FROM {table_name}").fetchone()[0]
    if last_measurement is None:
        last_measurement = 0
    new_measurement = last_measurement + 1

    c.executemany(f"INSERT INTO {table_name} (measurement, value) VALUES (?, ?)", [(new_measurement, value) for value in data])
    conn.commit()
    conn.close()

@socketio.on('send_data')
def send_data(message):
    global stop_reading
    stop_reading.set()  # Set the event flag to pause reading
    # Process the received data or perform other actions here
    print(f"Data received from client: {message}")
    # Resume data reading
    stop_reading.clear()


@socketio.on('send_serial')
def send_serial(command):
    global ser
    try:
        if command == 'FREQ100':
            ser.write('FREQ 100\r\n'.encode())
        elif command == 'FREQ100000':
            ser.write('FREQ 100000\r\n'.encode())
        elif command.startswith('VOLTage'):
            voltage = command.split(' ')[-1]
            ser.write(f'VOLT {voltage}\r\n'.encode())
        else:
            print('Invalid command')
    except Exception as e:
        print(f"Error sending serial command: {e}")

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=8000, debug=True)
