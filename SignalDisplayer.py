from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button
from dotenv import load_dotenv
import os

# Load variables from certs.env into os.environ
load_dotenv("certs.env")

# Global list to store incoming data
incoming_data = []
certificate_path = os.environ.get("CERTPEM")
private_key_path = os.environ.get("PRIVPEM")
ca_key_path = os.environ.get("CAPEM")
endpoint_path = os.environ.get("ENDPOINT")
signal_data_topic = os.environ.get("SIGNALDATATOPIC")
button_topic = os.environ.get("BUTTONTOPIC")
device_name_reciever = os.environ.get("DEVICENAMERECIEVER")

# Button event handlers
def button_callback1(event):
    print("Button 1 clicked")
    payload = json.dumps({"value": -1})
    mqtt_client.publish(button_topic, payload, 1)

def button_callback2(event):
    print("Button 2 clicked")
    payload = json.dumps({"value": 1})
    mqtt_client.publish(button_topic, payload, 1)
# Signal data handler
def on_message(msg):
    global incoming_data
    payload = msg.payload.decode('utf-8')
    json_data = json.loads(payload)
    incoming_data = json_data
    #print("Received message:", json_data)

# Create and configure the MQTT client
mqtt_client = AWSIoTMQTTClient(device_name_reciever)
mqtt_client.configureEndpoint(endpoint_path, 8883)
mqtt_client.configureCredentials(ca_key_path, private_key_path, certificate_path)

# Connect to AWS IoT
mqtt_client.connect()

# Subscribe to the topic
mqtt_client.subscribe(signal_data_topic, 1, lambda client, userdata, msg: on_message(msg))

# Non changing proeprties for the plot
plt.style.use('_mpl-gallery')
fig, ax = plt.subplots(figsize=(14, 8))

button_ax1 = plt.axes([0.35, 0.05, 0.15, 0.075]) # Button stuff
button1 = Button(button_ax1, '-1MHz')
button1.on_clicked(button_callback1)

button_ax2 = plt.axes([0.55, 0.05, 0.15, 0.075]) 
button2 = Button(button_ax2, '+1MHz')
button2.on_clicked(button_callback2)


plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

def format_freq_axis(value, _): # Hertz converter
    if value >= 1e9:
        return f"{value / 1e9:.3f} GHz"
    elif value >= 1e6:
        return f"{value / 1e6:.3f} MHz"
    elif value >= 1e3:
        return f"{value / 1e3:.3f} kHz"
    else:
        return f"{value:.3f} Hz"


def update(frame):
    ax.clear()  # Clear the existing plot

    if incoming_data:
        data = incoming_data['data_points']
        freq_axis = [point['freq_axis'] for point in data]
        spectrum_db = [point['spectrum_db'] for point in data]

        # Redraw the plot with new data
        ax.plot(freq_axis, spectrum_db, color="darkcyan")

        # Reapply plot parameters
        ax.set_xlabel('Frequency Axis')
        ax.set_ylabel('Spectrum (dB)')
        ax.set_title('Spectrum Plot')
        ax.set_xlim(freq_axis[0], freq_axis[-1])
        yMin = -60
        yMax = 60
        ax.set_ylim(yMin, yMax)
        ax.fill_between(freq_axis, yMin, spectrum_db, color='teal', alpha=0.8)
        ax.xaxis.set_major_formatter(FuncFormatter(format_freq_axis))

    

ani = FuncAnimation(fig, update, interval=10, cache_frame_data=False)  # Update the plot every interval

plt.show()