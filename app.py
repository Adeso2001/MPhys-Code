from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import DigitalIODirection
import threading
import time
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

board_num = 0

# Initialize device
try:
    device_info = DaqDeviceInfo(board_num)
    ai_info = device_info.get_ai_info()
    ao_info = device_info.get_ao_info()
    dio_info = device_info.get_dio_info()

    if not dio_info.port_info:
        logging.error("No digital I/O ports available on the device.")

    # Setup digital ports
    do_port = next((p for p in dio_info.port_info if p.supports_output), None)
    if do_port:
        logging.debug(f"Found Digital Output Port: {do_port.type}")
        if do_port.is_port_configurable:
            try:
                ul.d_config_port(board_num, do_port.type, DigitalIODirection.OUT)
                logging.debug(f"Configured port {do_port.type} as OUTPUT")
            except ULError as e:
                logging.error(f"Failed to configure digital port: {e}")
                digital_port = None
        else:
            logging.debug(f"Port {do_port.type} is not configurable.")
        digital_port = do_port.type
        logging.debug(f"Digital port set to: {digital_port}")
    else:
        logging.error("No Digital Output Port found.")
        digital_port = None

    di_port = next((p for p in dio_info.port_info if p.supports_input), None)
    if di_port:
        if di_port.is_port_configurable:
            try:
                ul.d_config_port(board_num, di_port.type, DigitalIODirection.IN)
                logging.debug(f"Configured port {di_port.type} as INPUT")
            except ULError as e:
                logging.error(f"Failed to configure digital input port: {e}")
                digital_input_port = None
        digital_input_port = di_port.type
        logging.debug(f"Digital input port set to: {digital_input_port}")
    else:
        digital_input_port = None
        logging.error("No Digital Input Port found.")

    ai_range = ai_info.supported_ranges[0]  # Select default range
except ULError as e:
    logging.error(f"Error initializing device: {e}")
    device_info = None
    ai_info = None
    ao_info = None
    digital_port = None
    digital_input_port = None
    ai_range = None

# Variables to hold the state
analog_inputs = {i: 0.0 for i in range(8)}
analog_outputs = {i: 0.0 for i in range(2)}
digital_outputs = {i: 0 for i in range(6)}
running = True  # Control the background thread

# Background thread to continuously read analog inputs
def update_analog_inputs():
    global analog_inputs, running
    while running:
        try:
            for i in range(8):
                if ai_info.resolution <= 16:
                    value = ul.v_in(board_num, i, ai_range)
                else:
                    value = ul.v_in_32(board_num, i, ai_range)
                analog_inputs[i] = value
        except ULError as e:
            logging.error(f"Error reading analog inputs: {e}")
        time.sleep(0.1)

input_thread = threading.Thread(target=update_analog_inputs)
input_thread.daemon = True
input_thread.start()

@app.route('/read_analog_input', methods=['GET'])
def read_analog_input():
    return jsonify(analog_inputs)

@app.route('/write_digital_output', methods=['POST'])
def write_digital_output():
    data = request.json
    channel = int(data.get('channel', 0))
    value = int(data.get('value', 0))
    
    if digital_port is None:
        logging.error('Digital port not configured.')
        return jsonify({'error': 'Digital port not configured'}), 500
    
    if channel not in digital_outputs:
        logging.error(f'Invalid channel {channel}.')
        return jsonify({'error': f'Invalid channel {channel}'}), 400
    
    try:
        ul.d_bit_out(board_num, digital_port, channel, value)
        digital_outputs[channel] = value
        logging.debug(f'Digital Output D{channel} set to {value}')
        return jsonify({'status': 'success', 'channel': channel, 'value': value})
    except ULError as e:
        error_message = f'ULError: {e}'
        if e.errorcode == 42:  # Error code for incorrect digital port configuration
            error_message += " The digital port may not be configured correctly for output."
            logging.error(error_message)
            # Attempt to reconfigure the digital port
            try:
                ul.d_config_port(board_num, digital_port, DigitalIODirection.OUT)
                logging.info(f"Reconfigured digital port {digital_port} as OUTPUT")
                # Retry the digital output operation
                ul.d_bit_out(board_num, digital_port, channel, value)
                digital_outputs[channel] = value
                logging.debug(f'Digital Output D{channel} set to {value} after reconfiguration')
                return jsonify({'status': 'success', 'channel': channel, 'value': value, 'message': 'Port reconfigured and output set'})
            except ULError as reconfig_error:
                error_message += f" Reconfiguration failed: {reconfig_error}"
                logging.error(error_message)
        else:
            logging.error(error_message)
        return jsonify({'error': error_message}), 500
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/write_analog_output', methods=['POST'])
def write_analog_output():
    data = request.json
    channel = int(data.get('channel', 0))
    value = float(data.get('value', 0.0))
    range_name = data.get('range', None)
    
    if ao_info is None:
        logging.error('Analog Output info is not available.')
        return jsonify({'error': 'Analog Output not supported on this device.'}), 500
    
    if not ao_info.supported_ranges:
        logging.error('No supported Analog Output ranges found.')
        return jsonify({'error': 'No Analog Output ranges available.'}), 500
    
    # Select the range based on user input
    if range_name:
        ao_range = next((r for r in ao_info.supported_ranges if r.name == range_name), None)
        if ao_range is None:
            logging.error(f'Invalid Analog Output range selected: {range_name}')
            return jsonify({'error': 'Invalid Analog Output range selected.'}), 400
    else:
        ao_range = ao_info.supported_ranges[0]  # Default range
    
    try:
        ul.v_out(board_num, channel, ao_range, value)
        analog_outputs[channel] = value
        logging.debug(f'Analog Output A{channel} set to {value} V with range {ao_range.name}')
        return jsonify({'status': 'success', 'channel': channel, 'value': value, 'range': ao_range.name})
    except ULError as e:
        logging.error(f'ULError: {e}')
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return jsonify({'error': 'An unexpected error occurred.'}), 500

@app.route('/set_input_range', methods=['POST'])
def set_input_range():
    data = request.json
    range_name = data.get('range', '')
    global ai_range
    try:
        for r in ai_info.supported_ranges:
            if r.name == range_name:
                ai_range = r
                return jsonify({'status': 'success', 'range': range_name})
        return jsonify({'error': 'Invalid range name'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/device_info', methods=['GET'])
def device_info_route():
    if device_info:
        info = {
            'board_num': board_num,
            'product_name': device_info.product_name,
            'unique_id': device_info.unique_id,
            'ai_ranges': [r.name for r in ai_info.supported_ranges],
            'ao_ranges': [r.name for r in ao_info.supported_ranges],
        }
        return jsonify(info)
    else:
        return jsonify({'error': 'Device not found'}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    global running
    running = False
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return jsonify({'status': 'Server shutting down...'})

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)