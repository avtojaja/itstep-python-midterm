import json
import os
from typing import List, Optional

STUDENTS_FILE = "students.json"


class Student:
    """სტუდენტის კლასი"""
    def __init__(self, name: str, roll_number: int, grade: str):
        # ინკაფსულირებული ველები
        self._name = None
        self._roll_number = None
        self._grade = None

        # setter-ების დაყენება
        self.name = name
        self.roll_number = roll_number
        self.grade = grade

    # Name თვისება
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("სახელი უნდა იყოს სტრინგი და არ უნდა იყოს ცარიელი.")
        self._name = value.strip()

    # roll_number თვისება
    @property
    def roll_number(self) -> int:
        return self._roll_number

    @roll_number.setter
    def roll_number(self, value: int):
        if not isinstance(value, int):
            raise ValueError("სიის ნომერი უნდა იყოს მთელი რიცხვი (int).")
        if value < 0:
            raise ValueError("სიის ნომერი უნდა იყოს დადებითი მთელი რიცხვი.")
        self._roll_number = value

    # Grade თვისება (ერთი სიმბოლო, A-F)
    @property
    def grade(self) -> str:
        return self._grade

    @grade.setter
    def grade(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("შეფასება უნდა იყოს სტრინგი (მაგ., A, B+, C-).")
        value = value.strip()
        if len(value) > 2:
            raise ValueError("შეფასება უნდა იყოს ერთი ან ორი სიმბოლო.")
        self._grade = value

    def to_dict(self) -> dict:
        """ობიექტის ლექსიკონად გარდაქმნა."""
        return {"type": "Student", "name": self.name, "roll_number": self.roll_number, "grade": self.grade}

    @classmethod
    def from_dict(cls, data: dict):
        """შექმნის Student ობიექტს ლექსიკონიდან."""
        return cls(name=data["name"], roll_number=int(data["roll_number"]), grade=data["grade"])

    def display(self) -> str:
        """ინფორმაციის გამოტანა სტუდენტის შესახებ."""
        return f"სახელი: {self.name}, სიის ნომერი: {self.roll_number}, შეფასება: {self.grade}"

    def __str__(self):
        return self.display()


# Subclass: HonorsStudent (inheritance, polymorphism)
class HonorsStudent(Student):
    """წარჩინებული სტუდენტი დამატებითი ატრიბუტით (მაგ., honors_note)."""
    def __init__(self, name: str, roll_number: int, grade: str, honors_note: str = ""):
        super().__init__(name, roll_number, grade)
        self._honors_note = honors_note.strip()

    @property
    def honors_note(self) -> str:
        return self._honors_note

    @honors_note.setter
    def honors_note(self, value: str):
        if not isinstance(value, str):
            raise ValueError("honors_note უნდა იყოს სტრინგი.")
        self._honors_note = value.strip()

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["type"] = "HonorsStudent"
        base["honors_note"] = self.honors_note
        return base

    @classmethod
    def from_dict(cls, data: dict):
        return cls(name=data["name"], roll_number=int(data["roll_number"]), grade=data["grade"], honors_note=data.get("honors_note", ""))

    def display(self) -> str:
        return f"[წარჩინებული] სახელი: {self.name}, სიის ნომერი: {self.roll_number}, შეფასება: {self.grade}, დახასიათება: {self.honors_note}"


# StudentManager კლასი
class StudentManager:
    """კლასი პასუხისმგებელია სტუდენტთა სიაზე და JSON ფაილზე (create/read/update/delete)."""
    def __init__(self, file_path: str = STUDENTS_FILE):
        self.file_path = file_path
        self.students: List[Student] = []
        self.load_from_file()

    def load_from_file(self):
        """ჩატვირთე students.json ფაილიდან. თუ ფაილი არ არსებობს, შეიქმნება ცარიელი ფაილი."""
        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump({"students": []}, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"ფაილის შექმნის შეცდომა: {e}")
            self.students = []
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.students = []
                for item in data.get("students", []):
                    if item.get("type") == "HonorsStudent":
                        self.students.append(HonorsStudent.from_dict(item))
                    else:
                        self.students.append(Student.from_dict(item))
        except json.JSONDecodeError:
            print("Error: JSON ფაილი დაზიანებული ან არასწორი ფორმატშია.")
            self.students = []
        except Exception as e:
            print(f"ფაილიდან წაკითხვის შეცდომა: {e}")
            self.students = []

    def save_to_file(self):
        """შენახვა JSON ფაილში."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"students": [s.to_dict() for s in self.students]}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"ფაილში შენახვის შეცდომა: {e}")

    def get_max_roll_number(self) -> int:
        """მაქსიმალური სიის ნომრის დადგენა სტუდენტების სიიდან. თუ სტუდენტების სია ცარიელია, ბრუნდება 0."""
        if not self.students:
            return 0
        return max(student.roll_number for student in self.students)

    def add_student(self, student: Student) -> bool:
        """ახალი სტუდენტის დამატება. სიის ნომერი გენერირდება ავტომატურად (მაქსიმუმს + 1)."""
        if student.roll_number == 0:
            student.roll_number = self.get_max_roll_number() + 1

        if self.find_by_roll_number(student.roll_number) is not None:
            print(f"Error: {student.roll_number} სიის ნომრით სტუდენტი უკვე არსებობს")
            return False
        self.students.append(student)
        self.save_to_file()
        return True

    def list_students(self) -> List[Student]:
        """აბრუნებს სტუდენტების სიას."""
        return list(self.students)

    def find_by_roll_number(self, roll_number: int) -> Optional[Student]:
        """ეძებს სტუდენტს სიის ნომრის მიხედვით."""
        for s in self.students:
            if s.roll_number == roll_number:
                return s
        return None

    def update_grade(self, roll_number: int, new_grade: str) -> bool:
        """განაახლებს სტუდენტის შეფასებას და საჭიროების შემთხვევაში ცვლის სტუდენტის ტიპს."""
        stud = self.find_by_roll_number(roll_number)
        if not stud:
            print("სტუდენტი ვერ მოიძებნა.")
            return False
        try:
            stud.grade = new_grade

            # მოწმდება შეფასება, და თუ ის არ უდრის A, A+ ან A-, სტატუსი იცვლება ჩვეულებრივ სტუდენტად
            if new_grade not in ["A", "A+", "A-"]:
                if isinstance(stud, HonorsStudent):
                    print(f"შეფასება '{new_grade}' არ არის წარჩინებული. სტუდენტი იცვლება ჩვეულებრივ სტუდენტად.")
                    self.students.remove(stud)
                    stud = Student(stud.name, stud.roll_number, stud.grade)
                    self.students.append(stud)

            self.save_to_file()
            return True
        except ValueError as e:
            print(f"ვალიდაციის შეცდომა: {e}")
            return False

    def delete_student(self, roll_number: int) -> bool:
        """სტუდენტის წაშლა სიის ნომრის მიხედვით."""
        stud = self.find_by_roll_number(roll_number)
        if not stud:
            print("სტუდენტი ვერ მოიძებნა.")
            return False
        self.students.remove(stud)
        self.save_to_file()
        return True

    def delete_data_file(self) -> bool:
        """JSON ფაილის წაშლა."""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                self.students = []
                print("students.json წაიშალა.")
                return True
            else:
                print("ფაილი არ არსებობს.")
                return False
        except Exception as e:
            print(f"ფაილის წაშლის შეცდომა: {e}")
            return False


# დამხმარე ფუნქციები: შეტანილი მონაცემების ვალიდაცია
def input_nonempty_string(prompt: str) -> str:
    """მოწმდება, რომ მომხმარებელმა არ შეიყვანა ცარიელი სტრიქონი."""
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("მონაცემი არ უნდა იყოს ცარიელი. სცადეთ თავიდან.")


def input_positive_int(prompt: str) -> int:
    """მოწმდება და ბრუნდება დადებითი მთელი რიცხვი."""
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if v > 0:
                return v
            else:
                print("გთხოვთ შეიყვანოთ დადებითი მთელი რიცხვი.")
        except ValueError:
            print("გთხოვთ შეიყვანოთ სრული (integer) მნიშვნელობა.")


def input_grade(prompt: str) -> str:
    """სავარაუდოდ grade არის A, B, C... ან A+, B-; ვალიდაცია - მაქსიმუმ 2 სიმბოლო."""
    while True:
        g = input(prompt).strip()
        if not g:
            print("შეფასება არ უნდა იყოს ცარიელი.")
            continue
        if len(g) > 2:
            print("შეფასება უნდა იყოს ერთი ან ორი სიმბოლო (მაგ., A, B+, C-).")
            continue
        return g


def input_roll_number_unique(manager: StudentManager) -> int:
    """მოწმდება, რომ სიის ნომერი არის უნიკალური."""
    while True:
        r = input_positive_int("შეიყვანეთ სიის ნომერი (roll_number): ")
        if manager.find_by_roll_number(r) is not None:
            print("სიის ეს ნომერი უკვე არსებობს, შეიყვანეთ სხვა ნომერი.")
            continue
        return r


# მენიუ
def main_menu():
    manager = StudentManager()
    print("== სტუდენტების მართვის სისტემა ==")

    while True:
        print()
        print("მენიუ:")
        print("1. ახალი სტუდენტის დამატება")
        print("2. ყველა სტუდენტის ნახვა")
        print("3. სტუდენტის ძებნა ნომრის მიხედვით")
        print("4. სტუდენტის შეფასების განახლება")
        print("5. სტუდენტის წაშლა")
        print("6. students.json ფაილის წაშლა")
        print("7. გამოსვლა")

        choice = input("აირჩიეთ ოპერაცია (1-7): ").strip()
        if choice == "1":
            # ახალი სტუდენტის დამატება
            try:
                name = input_nonempty_string("შეიყვანეთ სახელი და გვარი: ")
                grade = input_grade("შეიყვანეთ შეფასება (მაგ., A, B+, C-): ")
                is_honor = input("არის სტუდენტი წარჩინებული? (y/N): ").strip().lower()
                if is_honor == "y":
                    honors_note = input("შეიყვანეთ წარჩინებული სტუდენტის დახასიათება (არასავალდებულო): ").strip()
                    stud = HonorsStudent(name, 0, grade, honors_note)
                else:
                    stud = Student(name, 0, grade)
                if manager.add_student(stud):
                    print("სტუდენტი წარმატებით დაემატა.")
            except ValueError as e:
                print(f"ვალიდაციის შეცდომა: {e}")

        elif choice == "2":
            # ყველა სტუდენტის ნახვა
            students = manager.list_students()
            if not students:
                print("სისტემაში არ არიან სტუდენტები დამატებული.")
            else:
                print("\n--- სტუდენტების სია ---")
                for s in students:
                    print(s.display())

        elif choice == "3":
            # სტუდენტის ძებნა ნომრის მიხედვით
            roll_number = input_positive_int("შეიყვანეთ სიის ნომერი მის მოსაძებნად: ")
            stud = manager.find_by_roll_number(roll_number)
            if not stud:
                print("სტუდენტი ვერ მოიძებნა.")
            else:
                print("მონაცემები:")
                print(stud.display())

        elif choice == "4":
            # სტუდენტის შეფასების განახლება
            roll_number = input_positive_int("შეიყვანეთ სიის ნომერი შეფასების განახლებისთვის: ")
            if manager.find_by_roll_number(roll_number) is None:
                print("სტუდენტი არ მოიძებნა.")
            else:
                new_grade = input_grade("შეიყვანეთ ახალი შეფასება: ")
                if manager.update_grade(roll_number, new_grade):
                    print("შეფასება განახლდა.")

        elif choice == "5":
            # სტუდენტის წაშლა
            roll_number = input_positive_int("შეიყვანეთ სიის ნომერი წასაშლელად: ")
            confirm = input("დარწმუნებული ხართ რომ გსურთ წაშლა? (Y/n): ").strip().lower()
            if confirm == "" or confirm == "y":
                if manager.delete_student(roll_number):
                    print("სტუდენტი წაიშალა.")
            else:
                print("ოპერაცია გაუქმებულია.")

        elif choice == "6":
            # students.json ფაილის წაშლა
            confirm = input("დარწმუნებული ხართ რომ გსურთ students.json-ის წაშლა? (Y/n): ").strip().lower()
            if confirm == "" or confirm == "y":
                manager.delete_data_file()
            else:
                print("ოპერაცია გაუქმებულია.")

        elif choice == "7":
            print("გამოსვლა...")
            break
        else:
            print("არასწორი არჩევანი. შეიყვანეთ 1-7 შორის.")


if __name__ == "__main__":
    main_menu()
