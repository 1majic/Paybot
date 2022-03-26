import sqlite3
from datetime import datetime

# import self as self


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_name, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO users ('user_name', 'user_id') VALUES "
                                       "(?, ?)", (user_name, user_id,))

    def add_user_with_refer(self, user_name, user_id, referral):
        with self.connection:
            return self.cursor.execute("INSERT INTO users ('user_name', 'user_id', 'referral') VALUES "
                                       "(?, ?, ?)", (user_name, user_id, referral,))

    def get_user(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT user_name, user_id, purchases_num, balance FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result

    def get_users_id(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT user_id FROM users").fetchall()
            return result

    def get_users_username(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT user_name FROM users").fetchall()
            return result

    def get_user_id_from_username(self, username):
        with self.connection:
            result = self.cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (username,)).fetchall()
            return result

    def get_price_purchases(self, user_id):
        with self.connection:
            result = [i[0] for i in
                      self.cursor.execute("SELECT price FROM purchases WHERE user_id = ?", (user_id,)).fetchall()]
            return result

    def get_user_level(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,)).fetchall()[0][0]
            return result

    def get_items_list(self):
        with self.connection:
            response = self.cursor.execute(
                "SELECT id, category, subcategory, subject, item, price, link FROM items").fetchall()
            answer = []
            result = []
            for i in response:
                try:
                    ids, category_id, subcategory_id, subject_id, item_id, price, chat_id = i
                    category = self.category_name_from_id(category_id)
                    subcategory = self.subcategory_name_from_id(subcategory_id)
                    subject = self.subject_name_from_id(subject_id)
                    item = self.item_name_from_id(item_id)
                    string = f'#{ids} {category}|{subcategory}|{subject}|{item}|{price}|{chat_id}'
                    if string not in answer:
                        answer.append(string)

                    if len(answer) >= 30:
                        result.append('\n\n'.join(answer))
                        answer = []
                except:
                    print(f'Пропущен {i}')
            if answer:
                result.append('\n\n'.join(answer))
            return result

    def set_level(self, user_id, discount_level):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET level = ? WHERE user_id = ?", (discount_level, user_id,))

    def count_purchases(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT id FROM purchases WHERE user_id = ?", (user_id,)).fetchall()
            self.cursor.execute(
                "UPDATE users SET purchases_num = ? WHERE user_id = ?", (result, user_id,))
            return result

    def get_last_payment_id(self):
        with self.connection:
            result = self.cursor.execute("SELECT id FROM payments ORDER BY id DESC").fetchmany(1)
            return result[0][0]

    def add_payment(self, user_id, bill_id, sm):
        with self.connection:
            current_datetime = datetime.now()
            self.cursor.execute("INSERT INTO payments ('user_id', 'bill_id', 'sum', 'datetime') VALUES (?, ?, ?, ?)",
                                (user_id, bill_id, sm, current_datetime))

    def add_purchase(self, user_id, item_id, price, date):
        with self.connection:
            self.cursor.execute("INSERT INTO purchases ('user_id', 'item_id', 'price', 'date') VALUES (?, ?, ?, ?)",
                                (user_id, item_id, price, date))
            return self.cursor.lastrowid

    def get_payment(self, bill_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM payments WHERE bill_id = ?", (bill_id,)).fetchall()
            return result

    def get_payment_from_id(self, ids):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM payments WHERE id = ?", (int(ids),)).fetchall()
            return result

    def del_payment(self, bill_id):
        with self.connection:
            self.cursor.execute("DELETE FROM payments WHERE bill_id = ?", (bill_id,))

    def get_user_payments(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT id, sum, datetime FROM payments WHERE user_id = ? AND status = ?",
                                         (user_id, 'PAID',)).fetchall()
            return result

    def get_user_purchases(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT id, item_id, price, date FROM purchases WHERE user_id = ?",
                                         (user_id,)).fetchall()
            return result

    def get_upreferral(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT referral FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result[0][0]

    def get_user_balance(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result[0][0]

    def set_payment_status(self, bill_id, status):
        with self.connection:
            result = self.cursor.execute("UPDATE payments SET status = ? WHERE bill_id = ?", (status, bill_id,))

    def set_money(self, user_id, money):
        with self.connection:
            result = self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (money, user_id,))
            return result

    def set_purchase(self, user_id):
        with self.connection:
            result = self.cursor.execute("UPDATE users SET purchases_num = purchases_num + 1 WHERE user_id = ?",
                                         (user_id,))
            return result

    def get_free_courses(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM free_courses").fetchall()
            return result

    def get_categories(self):
        with self.connection:
            result = []
            for i in self.cursor.execute("SELECT category FROM items").fetchall():
                ans = [self.cursor.execute("SELECT category_name  FROM categories WHERE category_id = ?",
                                           (i[0],)).fetchall()[0][0], i[0]]
                if ans not in result:
                    result.append(ans)
            return result

    def get_subcategories(self, category):
        with self.connection:
            # category = self.category_id_from_name(category)
            result = []
            for i in self.cursor.execute("SELECT subcategory FROM items WHERE category = ?", (category,)).fetchall():
                ans = [self.cursor.execute("SELECT subcategory_name FROM subcategories WHERE subcategory_id = ?",
                                           (int(i[0]),)).fetchall()[0][0], i[0]]
                if ans not in result:
                    result.append(ans)
            return result

    def get_subjects(self, category, subcategory):
        with self.connection:
            # category = self.category_id_from_name(category)
            # subcategory = self.subcategory_id_from_name(subcategory)
            result = []
            for i in self.cursor.execute("SELECT subject FROM items WHERE category = ? AND subcategory = ?",
                                         (category, subcategory,)).fetchall():
                ans = [self.cursor.execute("SELECT subject_name FROM subjects WHERE subject_id = ?",
                                           (int(i[0]),)).fetchall()[0][0], i[0]]
                if ans not in result:
                    result.append(ans)
            return result

    def get_special_course(self, ids):
        with self.connection:
            return self.cursor.execute("SELECT name, price, description, photo FROM special_courses WHERE id = ?",
                                        (ids,)).fetchall()

    def get_special_courses(self):
        with self.connection:
            return self.cursor.execute("SELECT id, name, price FROM special_courses").fetchall()

    def get_items(self, category, subcategory, subject):
        result = []
        with self.connection:
            for ids, price in self.cursor.execute(
                    "SELECT item, price FROM items WHERE category = ? AND subcategory = ? AND subject = ?",
                    (category, subcategory, subject,)).fetchall():
                ans = self.cursor.execute("SELECT item_name FROM items_name_id WHERE item_id = ?",
                                        (int(ids),)).fetchall()[0][0]
                if ans == "Умскул":
                    result.insert(0, [ans, price, ids])
                else:
                    result.append([ans, price, ids])
            return result

    def get_item(self, category, subcategory, subject, item):
        with self.connection:
            result = self.cursor.execute(
                "SELECT description, price, photo FROM items WHERE category = ? AND subcategory = ? AND subject = ? AND item = ?",
                (category, subcategory, subject, item,)).fetchall()[0]
            return result

    def get_item_id_price(self, category, subcategory, subject, item):
        with self.connection:
            result = self.cursor.execute(
                "SELECT id, price FROM items WHERE category = ? AND subcategory = ? AND subject = ? AND item = ?",
                (category, subcategory, subject, item,)).fetchall()[0]
            return result

    def get_item_from_id(self, ids):
        with self.connection:
            result = self.cursor.execute(
                "SELECT item, description, price, photo FROM items WHERE id = ?",
                (ids,)).fetchall()[0]
            return result

    def get_chat_id(self, item_id):
        with self.connection:
            if '-' in item_id:
                result = self.cursor.execute(
                    "SELECT link FROM special_courses WHERE id = ?",
                    (str(item_id[1:]),)).fetchall()[0][0]

            elif '*' in item_id:
                result = self.cursor.execute(
                    "SELECT link FROM halfyear WHERE id = ?",
                    (str(item_id[1:]),)).fetchall()[0][0]
            else:
                result = self.cursor.execute(
                    "SELECT link FROM items WHERE id = ?",
                    ((str(item_id)),)).fetchall()[0][0]
            return result

    def category_name_from_id(self, category):
        return \
            self.cursor.execute("SELECT category_name FROM categories WHERE category_id = ?", (category,)).fetchall()[
                0][0]

    def subcategory_name_from_id(self, subcategory):
        return self.cursor.execute("SELECT subcategory_name FROM subcategories WHERE subcategory_id = ?",
                                   (subcategory,)).fetchall()[0][0]

    def subject_name_from_id(self, subject):
        return self.cursor.execute("SELECT subject_name FROM subjects WHERE subject_id = ?", (subject,)).fetchall()[0][
            0]

    def item_name_from_id(self, item_id):
        return self.cursor.execute("SELECT item_name FROM items_name_id WHERE item_id = ?", (item_id,)).fetchall()[0][
            0]

    def item_from_id(self, ids):
        if '-' in ids:
            args = self.cursor.execute("SELECT name, price FROM special_courses WHERE id = ?",
                                       (str(ids)[1:],)).fetchall()[0]
            name = args[0]
            return f"Рулетка | {name}"
        elif '*' in ids:
            args = self.cursor.execute("SELECT name, price FROM halfyear WHERE id = ?",
                                       (str(ids)[1:],)).fetchall()[0]
            name = args[0]
            return f"Полугодовой | {name}"
        else:
            args = self.cursor.execute("SELECT category, subcategory, subject, item FROM items WHERE id = ?",
                                       (str(ids),)).fetchall()[0]
            category = self.category_name_from_id(args[0])
            subcategory = self.subcategory_name_from_id(args[1])
            subject = self.subject_name_from_id(args[2])
            item = self.item_name_from_id(args[3])
            return f"{category} | {subcategory} | {subject} | {item}"

    # Добавление категории, подкатегории, предмета
    def add_category(self, category):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO categories ('category_name') VALUES (?)",
                (category,))

    def add_subcategory(self, subcategory):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO subcategories ('subcategory_name') VALUES (?)",
                (subcategory,))

    def add_subject(self, subject):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO subjects ('subject_name') VALUES (?)",
                (subject,))

    def add_item_name(self, item_name):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO items_name_id ('item_name') VALUES (?)",
                (item_name,))

    # Проверка существования категирии, подкатегории, предмета
    def check_category(self, category):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM categories WHERE category_name = ?", (category,)).fetchall()
            return bool(len(result))

    def check_subcategory(self, subcategory):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM subcategories WHERE subcategory_name = ?",
                                         (subcategory,)).fetchall()
            return bool(len(result))

    def check_subject(self, subject):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM subjects WHERE subject_name = ?", (subject,)).fetchall()
            return bool(len(result))

    def check_item_name(self, item_name):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM items_name_id WHERE item_name = ?", (item_name,)).fetchall()
            return bool(len(result))

    def add_item(self, category, subcategory, subject, item_name, description, price, chat_link):
        with self.connection:
            # Проверка существования категирии, подкатегории, предмета и добавление, если их нет
            if not self.check_category(category):
                self.add_category(category)
            if not self.check_subcategory(subcategory):
                self.add_subcategory(subcategory)
            if not self.check_subject(subject):
                self.add_subject(subject)
            if not self.check_item_name(item_name):
                self.add_item_name(item_name)

            # Получение id категирии, подкатегории, предмета
            category_id = \
                self.cursor.execute("SELECT category_id FROM categories WHERE category_name = ?",
                                    (category,)).fetchall()[
                    0][0]
            subcategory_id = self.cursor.execute("SELECT subcategory_id FROM subcategories WHERE subcategory_name = ?",
                                                 (subcategory,)).fetchall()[0][0]
            subject_id = \
                self.cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = ?", (subject,)).fetchall()[0][
                    0]
            item_id = \
                self.cursor.execute("SELECT item_id FROM items_name_id WHERE item_name = ?", (item_name,)).fetchall()[
                    0][
                    0]

            self.cursor.execute(
                "INSERT INTO items ('category', 'subcategory', 'subject', 'item','description', 'price', 'link') VALUES (?, ?, ?, ?, ?, ?, ?)",
                (category_id, subcategory_id, subject_id, item_id, description, price, chat_link,))

    def add_item_with_photo(self, category, subcategory, subject, item_name, description, photo, price, chat_link):
        with self.connection:
            # Проверка существования категирии, подкатегории, предмета и добавление, если их нет
            if not self.check_category(category):
                self.add_category(category)
            if not self.check_subcategory(subcategory):
                self.add_subcategory(subcategory)
            if not self.check_subject(subject):
                self.add_subject(subject)
            if not self.check_item_name(item_name):
                self.add_item_name(item_name)

            # Получение id категирии, подкатегории, предмета
            category_id = \
                self.cursor.execute("SELECT category_id FROM categories WHERE category_name = ?",
                                    (category,)).fetchall()[
                    0][0]
            subcategory_id = self.cursor.execute("SELECT subcategory_id FROM subcategories WHERE subcategory_name = ?",
                                                 (subcategory,)).fetchall()[0][0]
            subject_id = \
                self.cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = ?", (subject,)).fetchall()[0][
                    0]
            item_id = \
                self.cursor.execute("SELECT item_id FROM items_name_id WHERE item_name = ?", (item_name,)).fetchall()[
                    0][
                    0]

            self.cursor.execute(
                "INSERT INTO items ('category', 'subcategory', 'subject', 'item','description','photo', 'price', 'link') VALUES (?, ?, ?, ?, ?,?, ?, ?)",
                (category_id, subcategory_id, subject_id, item_id, description, photo, price, chat_link,))

    def add_item_image(self, photo, ids):
        with self.connection:
            self.cursor.execute(
                "UPDATE items SET photo = ? WHERE id = ?", (photo, ids,))

    def del_item(self, item_id):
        with self.connection:
            self.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))

    def get_referrals(self, user_id):
        with self.connection:
            result = [i[0] for i in
                      self.cursor.execute("SELECT user_name FROM users WHERE referral = ?", (user_id,)).fetchall()]
            return result

    def add_category_image(self, category, photo):
        with self.connection:
            self.cursor.execute("UPDATE categories SET category_photo = ? WHERE category_id = ?", (photo, category,))

    def add_halfyear_image(self, category, photo):
        with self.connection:
            self.cursor.execute("UPDATE halfyear SET photo = ? WHERE id = ?", (photo, category,))

    def add_special_course_image(self, category, photo):
        with self.connection:
            self.cursor.execute("UPDATE special_courses SET photo = ? WHERE id = ?", (photo, category,))

    def get_categories_ids_and_photos(self):
        with self.connection:
            result = self.cursor.execute("SELECT category_id, category_name FROM categories").fetchall()
            return result

    def add_subcategory_image(self, subcategory, photo):
        with self.connection:
            self.cursor.execute("UPDATE subcategories SET subcategory_photo = ? WHERE subcategory_id = ?",
                                (photo, subcategory,))

    def get_subcategories_ids_and_photos(self):
        with self.connection:
            result = self.cursor.execute("SELECT subcategory_id, subcategory_name FROM subcategories").fetchall()
            return result

    def add_subject_image(self, subject, photo):
        with self.connection:
            self.cursor.execute("UPDATE subjects SET subject_photo = ? WHERE subject_id = ?",
                                (photo, subject,))

    def get_subjects_ids_and_photos(self):
        with self.connection:
            result = self.cursor.execute("SELECT subject_id, subject_name FROM subjects").fetchall()
            return result

    def get_category_photo(self, category_id):
        with self.connection:
            result = self.cursor.execute("SELECT category_photo FROM categories WHERE category_id = ?",
                                         (category_id,)).fetchall()
            return result

    def get_subcategory_photo(self, subcategory_id):
        with self.connection:
            result = self.cursor.execute("SELECT subcategory_photo FROM subcategories WHERE subcategory_id = ?",
                                         (subcategory_id,)).fetchall()
            return result

    def get_subject_photo(self, subject_id):
        with self.connection:
            result = self.cursor.execute("SELECT subject_photo FROM subjects WHERE subject_id = ?",
                                         (subject_id,)).fetchall()
            return result

    def get_halfyear_courses(self):
        with self.connection:
            result = self.cursor.execute("SELECT id, name, price FROM halfyear").fetchall()
            return result

    def get_halfyear_course(self, ids):
        with self.connection:
            result = self.cursor.execute("SELECT name, price, description, photo FROM halfyear WHERE id = ?",
                                         (ids,)).fetchall()[0]
            return result

    def add_special_course(self, item_name, description, photo=None, price=None, chat_link=None):
        self.cursor.execute(
                "INSERT INTO special_courses ('name','description','photo', 'price', 'link') VALUES (?, ?, ?, ?, ?)",
                (item_name, description, photo, price, chat_link,))

    def add_halfyear(self, item_name, description, photo=None, price=None, chat_link=None):
        self.cursor.execute(
                "INSERT INTO halfyear ('name','description','photo', 'price', 'link') VALUES (?, ?, ?, ?, ?)",
                (item_name, description, photo, price, chat_link,))

    def get_special_course_list(self):
        with self.connection:
            response = self.cursor.execute(
                "SELECT id, name, price, link FROM special_courses").fetchall()
            answer = []
            result = []
            for i in response:
                try:
                    ids, name, price, chat_id = i
                    string = f'#{ids} {name}|{price}|{chat_id}'
                    if string not in answer:
                        answer.append(string)

                    if len(answer) >= 30:
                        result.append('\n\n'.join(answer))
                        answer = []
                except:
                    print(f'Пропущен {i}')
            if answer:
                result.append('\n\n'.join(answer))
            return result

    def del_special_course(self, item_id):
        with self.connection:
            self.cursor.execute("DELETE FROM special_courses WHERE id = ?", (item_id,))

    def get_halfyear_list(self):
        with self.connection:
            response = self.cursor.execute(
                "SELECT id, name, price, link FROM halfyear").fetchall()
            answer = []
            result = []
            for i in response:
                try:
                    ids, name, price, chat_id = i
                    string = f'#{ids} {name}|{price}|{chat_id}'
                    if string not in answer:
                        answer.append(string)

                    if len(answer) >= 30:
                        result.append('\n\n'.join(answer))
                        answer = []
                except:
                    print(f'Пропущен {i}')
            if answer:
                result.append('\n\n'.join(answer))
            return result

    def del_halfyear(self, item_id):
        with self.connection:
            self.cursor.execute("DELETE FROM halfyear WHERE id = ?", (item_id,))