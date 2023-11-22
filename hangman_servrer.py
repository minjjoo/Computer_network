import socket
import random
import os


SERVER_IP=''
SERVER_PORT=5555


def choose_word():
    words = ["apple", "banana", "orange", "grape", "melon",
             "pear", "coconut", "lemon", "peach", "mango", "lime" ,"plum"]
    return random.choice(words)

def display_word_with_blanks(word, guessed_letters):
    display = ""
    for letter in word:
        if letter in guessed_letters:
            display += letter
        else:
            display += "_"
    return display

def draw_hangman(incorrect_attempts):
    hangman_images = [
        "hangman0.jpg", "hangman1.jpg", "hangman2.jpg",
        "hangman3.jpg", "hangman4.jpg", "hangman5.jpg",
        "hangman6.jpg", "hangman7.jpg"
    ]
    if incorrect_attempts < len(hangman_images):
        return hangman_images[incorrect_attempts]
    else:
        return hangman_images[-1]

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)

    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")


    word_to_guess = choose_word()
    print(f"맞춰야 할 단어: {word_to_guess}")
    guessed_letters = []
    incorrect_attempts = 0
    

    while True:
        current_state = display_word_with_blanks(word_to_guess, guessed_letters)
        hangman_image = draw_hangman(incorrect_attempts)

        #print("Current State:", current_state)  # Print to the server console
        #print("Hangman Image:", hangman_image)  # Print to the server console

        # Send both current_state and hangman_image to the client
        update_message = f"{current_state}:{hangman_image}"
        client_socket.send(update_message.encode())

        play_again = client_socket.recv(1024).decode().lower()

        #맞추었을때 새로운 단어로 초기화하기  
        if play_again == "yes":  # Check if all letters are guessed
            word_to_guess = choose_word()
            print(f"맞춰야 할 단어: {word_to_guess}")
            guessed_letters = []
            incorrect_attempts = 0
            current_state = display_word_with_blanks(word_to_guess, guessed_letters)
            update_message = f"{current_state}:{hangman_image}"
            client_socket.send(update_message.encode())
        elif play_again == "no":
            break
        

        guess = client_socket.recv(1024).decode().lower()

        if guess not in guessed_letters:
            guessed_letters.append(guess)
            if guess not in word_to_guess:
                incorrect_attempts += 1

        if incorrect_attempts == 7:
            client_socket.send("You lose!".encode())
            client_socket.send(str(incorrect_attempts).encode())
            
            response = client_socket.recv(1024).decode().lower()
            if response == "yes":
                word_to_guess = choose_word()
                print(f"맞춰야 할 단어: {word_to_guess}")
                guessed_letters = []
                incorrect_attempts = 0

            elif response == "no":  # "no"를 받았을 때만 서버 종료
                break

    print("Closing connection...")
    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    main()
