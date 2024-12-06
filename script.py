import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading
import time
from queue import Queue
import random

class TwitchBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch Chat Bot")
        
        # IRC Configuration
        self.HOST = "irc.twitch.tv"
        self.PORT = 6667
        self.running = False
        self.message_queue = Queue()
        self.current_interval = 300  # Default 5 minutes
        
        self.setup_gui()
        
    def setup_gui(self):
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection Settings", padding="5")
        conn_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(conn_frame, text="Channel:").grid(row=0, column=0, padx=5, pady=5)
        self.channel_entry = ttk.Entry(conn_frame)
        self.channel_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="OAuth Token:").grid(row=1, column=0, padx=5, pady=5)
        self.oauth_entry = ttk.Entry(conn_frame, show="*")
        self.oauth_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Message Management Frame
        msg_frame = ttk.LabelFrame(self.root, text="Message Management", padding="5")
        msg_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.messages_text = scrolledtext.ScrolledText(msg_frame, width=40, height=10)
        self.messages_text.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ttk.Label(msg_frame, text="Separate messages with ~").grid(row=1, column=0, columnspan=2, padx=5)
        
        ttk.Label(msg_frame, text="Interval (seconds):").grid(row=2, column=0, padx=5, pady=5)
        self.interval_entry = ttk.Entry(msg_frame)
        self.interval_entry.insert(0, "300")
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Control Buttons
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=2, column=0, padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_bot)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_bot, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Status Label
        self.status_label = ttk.Label(self.root, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=3, column=0, pady=5)
        
    def connect_to_twitch(self):
        self.sock = socket.socket()
        self.sock.connect((self.HOST, self.PORT))
        
        oauth = self.oauth_entry.get()
        channel = self.channel_entry.get().lower()
        
        self.sock.send(f"PASS {oauth}\n".encode('utf-8'))
        self.sock.send(f"NICK {channel}\n".encode('utf-8'))
        self.sock.send(f"JOIN #{channel}\n".encode('utf-8'))
        
    def send_message(self, message):
        channel = self.channel_entry.get().lower()
        message_temp = f"PRIVMSG #{channel} :{message}\n"
        self.sock.send(message_temp.encode('utf-8'))
        
    def message_loop(self):
        while self.running:
            try:
                # Split messages by ~ and clean up any whitespace
                messages = [msg.strip() for msg in self.messages_text.get("1.0", tk.END).strip().split('~')]
                messages = [msg for msg in messages if msg]  # Remove empty messages
                
                if messages:
                    message = random.choice(messages)
                    self.send_message(message)
                    
                time.sleep(float(self.interval_entry.get()))
            except Exception as e:
                print(f"Error in message loop: {e}")
                self.running = False
                break
                
    def start_bot(self):
        try:
            self.connect_to_twitch()
            self.running = True
            self.status_label.config(text="Status: Running", foreground="green")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Start message sending thread
            self.message_thread = threading.Thread(target=self.message_loop)
            self.message_thread.daemon = True
            self.message_thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            
    def stop_bot(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", foreground="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        try:
            self.sock.close()
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TwitchBot(root)
    root.mainloop()