import sqlite3


class DataBase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        # Создание таблицы, если она еще не существует
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    language TEXT
                )
            ''')

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    coin_symbol TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
        ''')

        self.connection.commit()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, language):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO users (`user_id`, `language`) VALUES (?, ?)",
                (user_id, language)
            )

    def user_language(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `language` FROM `users` WHERE `user_id` = ?", (user_id,)
            ).fetchall()
            return result[0][0] if result else "en"

    def change_language(self, user_id):
        current = self.user_language(user_id)
        new_lang = "ru" if current == "en" else "en"

        with self.connection:
            self.cursor.execute(
                "UPDATE users SET language = ? WHERE user_id = ?", (new_lang, user_id)
            )

    def add_favorite(self, user_id, coin):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO favorites (user_id, coin_symbol) VALUES (?, ?)", (user_id, coin)
            )

    def get_favorites(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT coin_symbol FROM favorites WHERE user_id = ?",
                (user_id,)
            ).fetchall()
