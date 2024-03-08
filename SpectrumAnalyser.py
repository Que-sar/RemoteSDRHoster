import numpy as np
from rtlsdr import RtlSdr
import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from dotenv import load_dotenv
import os

class SpectrumAnalyser:
    def __init__(self):
        # Configured used variables        
        # Center frequency for the desired range (5 MHz)(from 500 KHz to 1.7GHz)
        self.center_frequency = 5e6
        self.min_frequency = 501e3  # 501 kHz
        self.max_frequency = 1.699e9  # 1.699 GHz

        # (min 250KHz max 3.2 MHz)
        self.sample_rate = 250000

        # (min 1024 - max 2560 MS/s, but it crashes there, limit to 2048(does not crash)) 
        # (decreased to preserve resources as it makes packets sent smaller)
        self.number_samples = 1024
        
        # Configure RTL-SDR
        self.sdr = RtlSdr()
        self.sdr.sample_rate = self.sample_rate
        self.sdr.center_freq = self.center_frequency
        self.sdr.gain = 'auto'
        
        # Configure AWS IoT
        # Load variables from certs.env into os.environ
        load_dotenv("certs.env")
        self.certificate_path = os.environ.get("CERTPEM")
        self.private_key_path = os.environ.get("PRIVPEM")
        self.ca_key_path = os.environ.get("CAPEM")
        self.endpoint_path = os.environ.get("ENDPOINT")
        self.signal_data_topic = os.environ.get("SIGNALDATATOPIC")
        self.button_topic = os.environ.get("BUTTONTOPIC")
        self.device_name_sender = os.environ.get("DEVICENAMESENDER")
        self.iot_client = AWSIoTMQTTClient(self.device_name_sender)
        self.iot_client.configureEndpoint(self.endpoint_path, 8883)
        self.iot_client.configureCredentials(self.ca_key_path, self.private_key_path, self.certificate_path)

        # Connect to AWS IoT
        self.iot_client.connect()
        
        # Subscribe to the frequency change topic
        self.iot_client.subscribe(self.button_topic, 1, self.on_frequency_change)

    def on_frequency_change(self, client, userdata, message):
        try:
            # Turn on yellow if frequency changes
            control_led(27, '1')
            payload = json.loads(message.payload)
            value = payload.get("value")

            # Check if frequency is within proper range(usable by the software defined radio dongle)
            new_value_holder = self.center_frequency + value * 1e6
            
            # Adjust the frequency
            if self.min_frequency <= new_value_holder <= self.max_frequency:
                self.center_frequency = new_value_holder

            # Update the SDR center frequency
            self.sdr.center_freq = self.center_frequency
            print(f"Center frequency changed to {self.center_frequency/1e6} MHz")
            # Turn yellow off when change is not anymore
            control_led(27, '0')

        except Exception as e:
            print(f"Error processing frequency change: {e}")

    def spectrum_processer(self):
        # Read samples
        samples = self.sdr.read_samples(self.number_samples)

        # Perform FFT (Fast Fourier Transform)
        spectrum = np.fft.fft(samples)

        # Get the amplitudes in dB (y coordinates)
        spectrum_db = 20 * np.log10(np.abs(spectrum))

        # Frequency axis (x coordinates)
        freq_axis = np.fft.fftfreq(self.number_samples, 1 / self.sample_rate) + self.center_frequency

        # Ensure that the frequency axis is in ascending order, breaks graph if not
        freq_axis.sort()

        # Prepare data for sending
        data_points = [{"freq_axis": freq, "spectrum_db": spectrum_db[i]} for i, freq in enumerate(freq_axis)]
        data = {"data_points": data_points}

        # Convert data to JSON
        payload = json.dumps(data, indent=4)

        return payload

    def send_data_to_iot_core(self, payload):
        try:
            # Publish payload to the data topic
            self.iot_client.publish(self.signal_data_topic, payload, 1)
        except Exception as e:
            print(f"Error publishing to AWS IoT Core: {e}")

    def spectrum_analyser(self):
        try:
            while True:
                payload = self.spectrum_processer()
                # Green light on if payload is being sent to AWS thing through MQTT
                control_led(22, '1')
                self.send_data_to_iot_core(payload)
                #time.sleep(1)  # Adjust as needed          

        finally:
            # Close RTL-SDR device
            self.sdr.close()
            # Off Green when stopped
            control_led(22, '0')
            # Disconnect from AWS IoT
            self.iot_client.disconnect()
            # Off red light when program stops running
            control_led(17, '0')
        
        
# Example usage for LED1 (GPIO 17 27 22)
# control_led(17, '1') Turn LED1 on
# control_led(17, '0') Turn LED1 off

def control_led(led_number, state):
    led_gpio_path = f"/sys/class/gpio/gpio{led_number}/value"
    with open(led_gpio_path, 'w') as file:
        file.write(state)

if __name__ == "__main__":
    # Red light on when running program
    control_led(17, '1')
    spectrum_analyser = SpectrumAnalyser()
    spectrum_analyser.spectrum_analyser()
