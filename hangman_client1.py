import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import socket
import threading
import os

class HangmanClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hangman Client")

        self.canvas = tk.Canvas(self.root, width=200, height=50)
        self.canvas.pack()

        initial_image_path = "hangman0.jpg"
        self.display_hangman(initial_image_path)

        self.guess_entry = tk.Entry(self.root)
        self.guess_entry.pack()

        self.guess_button = tk.Button(self.root, text="Guess", command=self.make_guess)
        self.guess_button.pack()


        self.server_ip='192.168.123.161'
        self.server_port=5555
        self.connect_to_server()

        # Create a thread for socket communication
        self.thread = threading.Thread(target=self.receive_updates, daemon=True)
        self.thread.start()

        self.root.mainloop()

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))

    def make_guess(self):
        guess = self.guess_entry.get().lower()
        if guess.isalpha() and len(guess) == 1:
            self.client_socket.send(guess.encode())

    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()

                # 데이터에 콜론이 있는지 확인
                if ':' in data:
                    current_state, hangman_image = data.split(':')
                    self.update_display(current_state, hangman_image)
                #else:
                    #print("Invalid data format received:", data)

            except socket.error:
                # Handle socket errors (e.g., server closed)
                print("Socket error or server closed.")
                break

    def update_display(self, current_state, hangman_image):
        # Display the hangman image in the tkinter window
        self.display_hangman(hangman_image)

        # Print the word and guessed letters to the terminal
        print("Current State:", current_state)

        #이겼을때
        if "_" not in current_state:  
            play_again = messagebox.askyesno("Game Over", "You win! Do you want to play again?")

            if play_again: #yes눌렀을때
                self.client_socket.send("yes".encode())
                self.initialize_game()  # 새로운 게임을 시작하도록 초기화

            else:          #no눌렀을떄
                self.client_socket.send("no".encode())
                self.root.destroy()

        #졌을때
        elif "You lose!" in current_state:
            #self.client_socket.send("no".encode())  # "You lose!" 메시지 전송
            #incorrect_attempts = int(self.client_socket.recv(1024).decode())  # 추가: 서버로부터 incorrect_attempts 값을 받아옴
            play_again = messagebox.askyesno("Game Over", "You lose! Do you want to play again?")
            if play_again:
                self.client_socket.send("yes".encode())
                self.initialize_game()  # 새로운 게임을 시작하도록 초기화
            else:
                self.client_socket.send("no".encode())
                #self.root.destroy()
        else:
            self.root.after(100, self.root.update)

    def initialize_game(self):
        self.guess_entry.delete(0, tk.END)  # 입력창 초기화
        #self.display_hangman("hangman0.jpg")  # 행맨 이미지 초기화

    def display_hangman(self, image_path):
        try:
            image = Image.open(image_path)
            resized_image = image.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

        # Calculate the center coordinates
            canvas_width = self.canvas.winfo_reqwidth()
            canvas_height = self.canvas.winfo_reqheight()
            x_center = (canvas_width - resized_image.width) // 2
            y_center = (canvas_height - resized_image.height) // 2

            self.canvas.create_image(x_center, y_center, anchor=tk.NW, image=photo)

        except FileNotFoundError:
            print(f"Image file not found: {image_path}")

if __name__ == "__main__":
    client = HangmanClient()
