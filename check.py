import socket
import pyaudio
import threading
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
kivy.require('1.11.1')  # Replace with your Kivy version

# Sender configuration
SENDER_HOST = '0.0.0.0'
SENDER_PORT = 12345
RECEIVER_IP = '192.168.17.219'
RECEIVER_PORT = 12346
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4024
MAX_PACKET_SIZE = 1096
server_ip = '192.168.17.219'
server_port = 12356

# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind((SENDER_HOST, RECEIVER_PORT))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ptt_active = False

def send_audio():
    while True:
        if ptt_active:
            data = sender_stream.read(CHUNK)
            for i in range(0, len(data), MAX_PACKET_SIZE):
                chunk = data[i:i+MAX_PACKET_SIZE]
                sender_socket.sendto(chunk, (RECEIVER_IP, RECEIVER_PORT))

def receive_audio():
    while True:
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_thread = threading.Thread(target=receive_audio)
sender_thread.start()
receiver_thread.start()

# class PTTApp(App):
#     def build(self):
#         button = Button(text="Push to Talk", on_press=self.key_pressed, on_release=self.key_released)
#         return button

#     def key_pressed(self, instance):
#         global ptt_active
#         client_socket.sendto(b'high', (server_ip, server_port))
#         ptt_active = True
#         print("Talking...")

#     def key_released(self, instance):
#         global ptt_active
#         client_socket.sendto(b'low', (server_ip, server_port))
#         ptt_active = False
#         print("Not talking...")

class PTTApp(App):
    def build(self):
        button = ToggleButton(text="Push to Talk")
        button.bind(state=self.on_button_state)
        return button

    def on_button_state(self, instance, value):
        global ptt_active
        if  value == "down":  # Button is pressed
            client_socket.sendto(b'high', (server_ip, server_port))
            ptt_active = True
            print("Talking...")
        else:  # Button is released
            client_socket.sendto(b'low', (server_ip, server_port))
            ptt_active = False
            print("Not talking...")

if __name__ == '__main__':
    PTTApp().run()
