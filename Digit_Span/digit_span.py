import tkinter as tk
import random

class MemoryGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Hafıza Oyunu")
        self.master.geometry("400x650")
        self.master.config(bg="white")

        self.level = None
        self.generated_numbers = []
        self.filtered_numbers = []
        self.user_input = ""

        self.streak = 0
        self.correct_count = 0
        self.wrong_count = 0

        self.create_widgets()

    def create_widgets(self):
        # Başlık
        self.title_label = tk.Label(self.master, text="Hafıza Oyunu", font=("Arial", 24, "bold"), fg="#2C3E50", bg="white")
        self.title_label.pack(pady=10)

        # Seviye seçimi
        self.level_label = tk.Label(self.master, text="Seviye Seç (4-10):", font=("Arial", 14), fg="#2C3E50", bg="white")
        self.level_label.pack(pady=5)

        self.level_buttons_frame = tk.Frame(self.master, bg="white")
        self.level_buttons_frame.pack()

        for i in range(4, 11):
            btn = tk.Button(self.level_buttons_frame, text=str(i), font=("Arial", 12, "bold"),
                            width=3, height=1, command=lambda x=i: self.set_level(x),
                            bg="#3498DB", fg="white", activebackground="#2980B9")
            btn.grid(row=0, column=i-4, padx=5, pady=5)

        # Gösterim için sayı label
        self.number_label = tk.Label(self.master, text="", font=("Arial", 40, "bold"), fg="#E67E22", bg="white")
        self.number_label.pack(pady=20)

        # Sayaçlar
        self.stats_label = tk.Label(self.master, text="Doğru: 0 | Yanlış: 0 | Streak: 0",
                                    font=("Arial", 12), fg="#2C3E50", bg="white")
        self.stats_label.pack(pady=10)

        # Kullanıcı giriş ekranı
        self.entry_label = tk.Label(self.master, text="Sonucu gir:", font=("Arial", 14), fg="#2C3E50", bg="white")
        self.entry_label.pack(pady=5)

        self.input_display = tk.Label(self.master, text="", font=("Arial", 20, "bold"),
                                      fg="#2C3E50", bg="#ECF0F1", width=12, height=2, relief="ridge")
        self.input_display.pack(pady=5)

        # Numaratör
        self.keypad_frame = tk.Frame(self.master, bg="white")
        self.keypad_frame.pack()

        buttons = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("C", 3, 0), ("0", 3, 1), ("OK", 3, 2)
        ]

        for (text, row, col) in buttons:
            btn = tk.Button(self.keypad_frame, text=text, font=("Arial", 14, "bold"),
                            width=5, height=2,
                            command=lambda t=text: self.keypad_press(t),
                            bg="#1ABC9C", fg="white", activebackground="#16A085")
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Mesaj kutusu
        self.message_label = tk.Label(self.master, text="", font=("Arial", 16, "bold"), fg="#2C3E50", bg="white")
        self.message_label.pack(pady=10)

        # Next butonu
        self.next_button = tk.Button(self.master, text="Next", font=("Arial", 14, "bold"),
                                     bg="#9B59B6", fg="white", activebackground="#8E44AD",
                                     state="disabled", command=self.start_game)
        self.next_button.pack(pady=10)

    def set_level(self, lvl):
        self.level = lvl
        self.start_game()

    def start_game(self):
        self.user_input = ""
        self.input_display.config(text="")
        self.message_label.config(text="")
        self.next_button.config(state="disabled")

        self.generated_numbers = self.generate_numbers()
        self.filtered_numbers = self.filter_numbers(self.generated_numbers)

        # Eğer uzunluk tutmazsa tekrar üret
        while len(self.filtered_numbers) != self.level:
            self.generated_numbers = self.generate_numbers()
            self.filtered_numbers = self.filter_numbers(self.generated_numbers)

        self.show_numbers(self.generated_numbers, 0)

    def generate_numbers(self):
        length = random.randint(self.level + 1, self.level + 4)  # biraz uzun üret
        numbers = [random.randint(1, 9)]  # ilk sayı asla 0 değil
        for _ in range(length - 1):
            numbers.append(random.randint(0, 9))
        return numbers

    def filter_numbers(self, numbers):
        result = [numbers[0]]
        for i in range(1, len(numbers)):
            if numbers[i] > numbers[i-1]:
                result.append(numbers[i])
        return result

    def show_numbers(self, numbers, index):
        if index < len(numbers):
            self.number_label.config(text=str(numbers[index]))
            self.master.after(1000, self.show_numbers, numbers, index+1)
        else:
            self.number_label.config(text="")
            self.message_label.config(text="Sonucu gir!")

    def keypad_press(self, key):
        if key == "C":
            self.user_input = self.user_input[:-1]
        elif key == "OK":
            self.check_result()
            return
        else:
            self.user_input += key

        self.input_display.config(text=self.user_input)

    def check_result(self):
        if self.user_input == "".join(map(str, self.filtered_numbers)):
            self.message_label.config(text="✅ Doğru!", fg="#27AE60")
            self.streak += 1
            self.correct_count += 1
        else:
            self.message_label.config(text=f"❌ Yanlış! Doğru: {''.join(map(str, self.filtered_numbers))}",
                                      fg="#C0392B")
            self.streak = 0
            self.wrong_count += 1

        self.stats_label.config(
            text=f"Doğru: {self.correct_count} | Yanlış: {self.wrong_count} | Streak: {self.streak}"
        )
        self.next_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()