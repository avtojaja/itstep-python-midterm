import json
import os

# ===============================
# BankAccount კლასი
# ===============================
class BankAccount:
    """კლასი, რომელიც წარმოადგენს მომხმარებლის ბანკის ანგარიშს"""
    def __init__(self, account_number, fullname, password, balance=0.0):
        self.account_number = account_number
        self.fullname = fullname
        self.password = password
        self._balance = balance  # ინკაფსულაცია

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        """თანხის შეტანა ანგარიშზე"""
        if amount <= 0:
            print("თანხა უნდა იყოს დადებითი!")
            return False
        self._balance += amount
        print(f"{amount} შეიტანილია ანგარიშზე. მიმდინარე ბალანსი: {self._balance}")
        return True

    def withdraw(self, amount):
        """თანხის გატანა ანგარიშიდან"""
        if amount <= 0:
            print("თანხა უნდა იყოს დადებითი!")
            return False
        if amount > self._balance:
            print("ბალანსი არასაკმარისია!")
            return False
        self._balance -= amount
        print(f"{amount} გატანილია ანგარიშიდან. დარჩენილი ბალანსი: {self._balance}")
        return True

# ===============================
# Bank კლასი
# ===============================
class Bank:
    """კლასი, რომელიც მართავს ყველა ანგარიშს და JSON ფაილს"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.accounts = []
        self.load_accounts()

    def load_accounts(self):
        """JSON ფაილიდან ანგარიშების ჩატვირთვა"""
        if not os.path.exists(self.file_path):
            self.save_accounts()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.accounts = []
                for acc in data.get("accounts", []):
                    self.accounts.append(BankAccount(
                        acc["account_number"], acc["fullname"], acc["password"], acc["balance"]
                    ))
        except Exception as e:
            print(f"ფაილის წაკითხვის შეცდომა: {e}")
            self.accounts = []

    def save_accounts(self):
        """ანგარიშების შენახვა JSON ფაილში"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"accounts": [
                    {
                        "account_number": acc.account_number,
                        "fullname": acc.fullname,
                        "password": acc.password,
                        "balance": acc.balance
                    }
                    for acc in self.accounts
                ]}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"ფაილის შენახვის შეცდომა: {e}")

    def find_account(self, account_number):
        """ანგარიშის მოძებნა ნომრით"""
        for acc in self.accounts:
            if acc.account_number == account_number:
                return acc
        return None

    def add_account(self, account_number, fullname, password, balance=0.0):
        """ახალი ანგარიშის დამატება"""
        if self.find_account(account_number):
            print("ანგარიში უკვე არსებობს!")
            return False
        if len(account_number) != 12 or not account_number.isdigit():
            print("ანგარიშის ნომერი უნდა იყოს 12 ციფრი!")
            return False
        self.accounts.append(BankAccount(account_number, fullname, password, balance))
        self.save_accounts()
        print(f"ანგარიში {account_number} წარმატებით შეიქმნა.")
        return True

    def delete_account(self, account_number, password):
        """ანგარიშის გაუქმება"""
        acc = self.find_account(account_number)
        if not acc:
            print("ანგარიში ვერ მოიძებნა!")
            return False
        if acc.password != password:
            print("პაროლი არასწორია!")
            return False
        self.accounts.remove(acc)
        self.save_accounts()
        print(f"ანგარიში {account_number} გაუქმდა.")
        return True

# ===============================
# ATM კლასი
# ===============================
class ATM:
    """ბანკომატის ინტერფეისი მომხმარებლისთვის"""
    def __init__(self, bank):
        self.bank = bank
        self.current_account = None

    def login(self):
        """მომხმარებლის ავტორიზაცია"""
        account_number = input("შეიყვანეთ 12-ციფრიანი ანგარიშის ნომერი: ").strip()
        account = self.bank.find_account(account_number)
        if not account:
            print("ანგარიში ვერ მოიძებნა!")
            return False
        password = input("შეიყვანეთ პაროლი: ").strip()
        if password != account.password:
            print("პაროლი არასწორია!")
            return False
        self.current_account = account
        print(f"კეთილი იყოს თქვენი მობრძანება, {account.fullname}!")
        return True

    def register(self):
        print("\nანგარიშის რეგისტრაცია")
        account_number = input("შეიყვანეთ 12-ციფრიანი ანგარიში: ").strip()
        fullname = input("შეიყვანეთ თქვენი სრული სახელი: ").strip()
        password = input("შეიყვანეთ პაროლი: ").strip()
        balance = 0.0
        try:
            balance = float(input("შეიყვანეთ საწყისი ბალანსი: ").strip())
        except ValueError:
            print("არასწორი თანხა, ბალანსი 0.0")
        self.bank.add_account(account_number, fullname, password, balance)

    def transfer(self, withdrawal_fee=0.5):
        target_acc_num = input("შეიყვანეთ მიმღები ანგარიშის ნომერი: ").strip()
        target_acc = self.bank.find_account(target_acc_num)
        if not target_acc:
            print("მიმღები ანგარიში ვერ მოიძებნა!")
            return
        try:
            amount = float(input("შეიყვანეთ გადასარიცხი თანხა: ").strip())
        except ValueError:
            print("გთხოვთ შეიყვანოთ რიცხვი!")
            return
        if self.current_account.withdraw(amount + withdrawal_fee):
            target_acc.deposit(amount)
            self.bank.save_accounts()
            print(f"{amount} წარმატებით გადარიცხულია ანგარიშზე {target_acc_num} (საკომისიო: {withdrawal_fee})")

    def run(self):
        """აპლიკაციის მთავარი ციკლი"""
        print("მოგესალმებით ბანკომატში!")
        while True:
            print()
            print("1. ავტორიზაცია")
            print("2. რეგისტრაცია")
            print("3. გამოსვლა")
            choice = input("აირჩიეთ ოპერაცია: ").strip()
            if choice == "1":
                if not self.login():
                    continue
                break
            elif choice == "2":
                self.register()
            elif choice == "3":
                return
            else:
                print("არასწორი არჩევანი!")

        while True:
            print()
            print("1. ბალანსის შემოწმება")
            print("2. თანხის შეტანა")
            print("3. თანხის გატანა")
            print("4. გადარიცხვა")
            print("5. ანგარიშის გაუქმება")
            print("6. გამოსვლა")
            choice = input("აირჩიეთ ოპერაცია: ").strip()
            if choice == "1":
                print(f"მიმდინარე ბალანსი: {self.current_account.balance}")
            elif choice == "2":
                try:
                    amount = float(input("შეიყვანეთ თანხა: ").strip())
                    if self.current_account.deposit(amount):
                        self.bank.save_accounts()
                except ValueError:
                    print("არასწორი თანხა!")
            elif choice == "3":
                try:
                    amount = float(input("შეიყვანეთ თანხა: ").strip())
                    if self.current_account.withdraw(amount):
                        self.bank.save_accounts()
                except ValueError:
                    print("არასწორი თანხა!")
            elif choice == "4":
                self.transfer()
            elif choice == "5":
                confirm = input("გსურთ ანგარიში გაუქმდეს? (Y/n): ").strip().lower()
                if confirm == "" or confirm == "y":
                    if self.bank.delete_account(self.current_account.account_number, self.current_account.password):
                        print("ანგარიშიდან გამოსვლა...")
                        break
            elif choice == "6":
                print("თქვენ გამოხვედით ანგარიშიდან...")
                break
            else:
                print("არასწორი არჩევანი!")


# ===============================
# პროგრამის დაწყება
# ===============================
if __name__ == "__main__":
    bank_file = "accounts.json"
    bank = Bank(bank_file)
    atm = ATM(bank)
    atm.run()
