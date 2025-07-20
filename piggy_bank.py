import json
import os
from datetime import datetime, timedelta


class Goal:
    def __init__(self, name, target, category, deadline=None):
        self.name = name
        self.target = target
        self.balance = 0.0
        self.category = category
        self.status = "В процессе"
        self.deadline = deadline
        self.history = []

    def update_balance(self, amount):
        if amount > 0 and self.balance + amount > self.target:
            print("Ошибка: Сумма превышает целевую")
            return False

        self.balance += amount
        self.history.append({
            "date": datetime.now().isoformat(),
            "amount": amount,
            "operation": "Пополнение" if amount > 0 else "Снятие"
        })

        # Обновление статуса
        if self.balance >= self.target:
            self.status = "Выполнена"

        # Проверка процентов (50%, 75%, 100%)
        progress = self.get_progress()
        if progress >= 100:
            print(f"Поздравляем! Цель '{self.name}' достигнута!")
        elif progress >= 75:
            print(f"Отлично! Цель '{self.name}' выполнена на 75%!")
        elif progress >= 50:
            print(f"Хорошо! Цель '{self.name}' выполнена на 50%!")

        return True

    def get_progress(self):
        return (self.balance / self.target) * 100

    def predict_deadline(self, avg_frequency=7):
        if self.balance <= 0:
            return None

        avg_contribution = abs(sum(
            [item['amount'] for item in self.history if item['amount'] > 0]
        ) / len(self.history))

        remaining = self.target - self.balance
        weeks_needed = remaining / avg_contribution
        return datetime.now() + timedelta(weeks=weeks_needed * avg_frequency)


class PiggyBank:
    def __init__(self, filename="goals.json"):
        self.filename = filename
        self.goals = []
        self.load_data()

    def add_goal(self, name, target, category, deadline=None):
        if any(g.name == name for g in self.goals):
            print("Ошибка: Цель с таким именем уже существует")
            return

        try:
            target = float(target)
            new_goal = Goal(name, target, category, deadline)
            self.goals.append(new_goal)
            self.save_data()
            print(f"Цель '{name}' добавлена!")
        except ValueError:
            print("Ошибка: Некорректная сумма")

    def update_balance(self, name, amount):
        try:
            amount = float(amount)
            for goal in self.goals:
                if goal.name == name:
                    if goal.update_balance(amount):
                        self.save_data()
                    return
            print("Ошибка: Цель не найдена")
        except ValueError:
            print("Ошибка: Некорректная сумма")

    def delete_goal(self, name):
        self.goals = [g for g in self.goals if g.name != name]
        self.save_data()
        print(f"Цель '{name}' удалена!")s

    def get_total_progress(self):
        total_target = sum(g.target for g in self.goals)
        total_balance = sum(g.balance for g in self.goals)
        return (total_balance / total_target) * 100 if total_target > 0 else 0

    def save_data(self):
        data = []
        for goal in self.goals:
            data.append({
                "name": goal.name,
                "target": goal.target,
                "balance": goal.balance,
                "category": goal.category,
                "status": goal.status,
                "deadline": goal.deadline.isoformat() if goal.deadline else None,
                "history": goal.history
            })

        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for item in data:
                    goal = Goal(
                        item['name'],
                        item['target'],
                        item['category'],
                        datetime.fromisoformat(item['deadline']) if item['deadline'] else None
                    )
                    goal.balance = item['balance']
                    goal.status = item['status']
                    goal.history = item['history']
                    self.goals.append(goal)
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")


# Пример использования
if __name__ == "__main__":
    bank = PiggyBank()

    while True:
        print("\n1. Добавить цель")
        print("2. Пополнить цель")
        print("3. Удалить цель")
        print("4. Показать все цели")
        print("5. Прогноз завершения")
        print("6. Общий прогресс")
        print("7. Выйти")

        choice = input("Выберите действие: ")

        if choice == "1":
            name = input("Название цели: ")
            target = input("Целевая сумма: ")
            category = input("Категория: ")
            deadline = input("Дедлайн (ГГГГ-ММ-ДД или пропуск): ")
            bank.add_goal(
                name,
                target,
                category,
                datetime.fromisoformat(deadline) if deadline else None
            )

        elif choice == "2":
            name = input("Название цели: ")
            amount = input("Сумма: ")
            bank.update_balance(name, amount)

        elif choice == "3":
            name = input("Название цели для удаления: ")
            bank.delete_goal(name)

        elif choice == "4":
            for goal in bank.goals:
                print(f"\n{goal.name} ({goal.category})")
                print(f"Прогресс: {goal.get_progress():.2f}%")
                print(f"Статус: {goal.status}")
                if goal.deadline:
                    print(f"Дедлайн: {goal.deadline.strftime('%d.%m.%Y')}")

        elif choice == "5":
            name = input("Название цели: ")
            for goal in bank.goals:
                if goal.name == name:
                    prediction = goal.predict_deadline()
                    if prediction:
                        print(f"Прогноз завершения: {prediction.strftime('%d.%m.%Y')}")
                    else:
                        print("Недостаточно данных для прогноза")
                    break
            else:
                print("Цель не найдена")

        elif choice == "6":
            print(f"Общий прогресс: {bank.get_total_progress():.2f}%")

        elif choice == "7":
            bank.save_data()
            print("Данные сохранены. Выход...")
            break