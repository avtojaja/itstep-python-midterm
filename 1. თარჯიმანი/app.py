import json
import os

# ===============================
# TranslationDictionary კლასი
# ===============================
class TranslationDictionary:
    """კლასი, რომელიც მართავს თარგმანების JSON ლექსიკონს"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.translations = []  # list of dicts

        # თუ ფაილი არსებობს, ჩაიტვირთოს
        if os.path.exists(file_path):
            self.load_file()
        else:
            # შექმნას ცარიელი JSON
            self.save_file()

    def load_file(self):
        """JSON ფაილიდან თარგმანების ჩატვირთვა"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.translations = data.get("translations", [])
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            self.translations = []

    def save_file(self):
        """თარგმანების შენახვა JSON ფაილში"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"translations": self.translations}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error writing JSON file: {e}")

    def translate(self, pair, word):
        """სიტყვის თარგმანის მოძებნა"""
        for t in self.translations:
            if t['pair'] == pair and t['source'].lower() == word.lower():
                return t['target']
        return None

    def add_translation(self, pair, source, target):
        """ახალი თარგმანის დამატება"""
        self.translations.append({'pair': pair, 'source': source, 'target': target})
        self.save_file()


# ===============================
# Translator კლასი
# ===============================
class Translator:
    """თარჯიმანის აპლიკაცია"""
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.language_pairs = [
            'ქართული-ინგლისური',
            'ინგლისური-ქართული',
            'ქართული-ესპანური',
            'ესპანური-ქართული'
        ]
        self.current_pair = None

    def choose_language_pair(self):
        """ენის წყვილის არჩევა"""
        while True:
            print("\nაირჩიეთ ენების წყვილი:")
            for idx, pair in enumerate(self.language_pairs, start=1):
                print(f"{idx}. {pair}")
            print("0. გამოსვლა")

            choice = input("შეიყვანეთ ნომერი: ").strip()
            if choice == '0':
                return False
            try:
                choice = int(choice)
                if 1 <= choice <= len(self.language_pairs):
                    self.current_pair = self.language_pairs[choice-1]
                    print(f"არჩეული ენების წყვილი: {self.current_pair}")
                    return True
                else:
                    print("არასწორი არჩევანი!")
            except ValueError:
                print("გთხოვთ, შეიყვანოთ ციფრი!")

    def run(self):
        """აპლიკაციის მთავარი ციკლი"""
        print("კეთილი იყოს თქვენი მობრძანება თარჯიმანის აპლიკაციაში!")

        if not self.choose_language_pair():
            print("პროგრამიდან გასვლა...")
            return

        while True:
            # სიტყვის/ფრაზის შეყვანა
            word = input(f"\nშეიყვანეთ თარგმანის სიტყვა/ფრაზა ({self.current_pair.split('-')[0]} -> {self.current_pair.split('-')[1]}) ან 'change' ენების შეცვლისთვის, 'exit' გასასვლელად: ").strip()
            if not word:
                print("მონაცემი ცარიელია!")
                continue
            if word.lower() == "exit":
                print("პროგრამიდან გასვლა...")
                break
            if word.lower() == "change":
                # ენების შეცვლა, default არის Y
                response = input("გსურთ შეცვალოთ ენების წყვილი? (Y/n): ").strip().lower()
                if response == '' or response == 'y':
                    if not self.choose_language_pair():
                        print("პროგრამიდან გასვლა...")
                        break
                continue

            # თარგმანის მოძებნა
            result = self.dictionary.translate(self.current_pair, word)
            if result:
                print(f"თარგმანი: {result}")
            else:
                print("სიტყვა არ მოიძებნა ლექსიკონში.")
                add = input("გსურთ დაამატოთ თარგმანი? (Y/n): ").strip().lower()
                if add == '' or add == 'y':
                    new_translation = input(f"შეიყვანეთ თარგმანი ({self.current_pair.split('-')[1]} ენაზე): ").strip()
                    if new_translation:
                        self.dictionary.add_translation(self.current_pair, word, new_translation)
                        print("თარგმანი დაემატა JSON ლექსიკონში.")
                    else:
                        print("შეყვანილი თარგმანი ცარიელია, ვერ დაემატა.")


# ===============================
# პროგრამის დაწყება
# ===============================
if __name__ == "__main__":
    dict_file = "dictionary.json"
    translation_dict = TranslationDictionary(dict_file)
    translator = Translator(translation_dict)
    translator.run()
