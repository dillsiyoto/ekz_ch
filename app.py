from flask import(
    Flask,
    redirect,
    request,
    render_template,
    url_for,
    session # Импортируем модули из фласка
)
import os # Импортируем ос для работы с файлами
import sqlite3 # Импортируем библиотеку для работы с бд
from models.users import start_db # импортируем функцию из папки модель

UPLOAD_FOLDER = os.path.join('static','images') # Назначаем папку, куда будут загружаться фото

app = Flask(__name__) # Создаем объект фласка
app.secret_key = 'parol' # Устанавливаем пароль
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

start_db() # Запускаем функцию, которая создаст бд

@app.route('/', methods=['GET', 'POST']) # Главная страница, где будут видны все посты
def get_home():
    conn = sqlite3.connect('post.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM post')
    spisok:list = cursor.fetchall()
    conn.close()
    return render_template('home.html', spisok = spisok)


@app.route('/reg', methods=['GET', 'POST']) # Страница регистрации
def get_reg():
    if request.method == 'POST':
        login = request.form.get('login', type=str)
        email = request.form.get('email', type=str)
        password = request.form.get('password', type=str)
        session['login'] = request.form.get('login')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (login, email, password) VALUES (?, ?, ?)', (login, email, password))

        conn.commit()
        conn.close()
        return redirect(url_for('get_home'))
    return render_template('reg.html')


@app.route('/log', methods=['GET', 'POST']) # Страница входа
def get_log():
    if request.method == 'POST':
        login = request.form.get('login', type=str)
        password = request.form.get('password', type=str)
        session['login'] = request.form.get('login')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password))
        user = cursor.fetchone()

        if user:
            return redirect(url_for('get_profile'))
        else:
            error_message = 'Неправильный логин или пароль'
            return render_template('log.html', error = error_message)
        
        conn.close()
    return render_template('log.html')


@app.route('/profile', methods=['GET','POST']) # Страница профиля, где виден логин и заказы
def get_profile():
    login = session.get('login', 'Гость')
    conn = sqlite3.connect('calling.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM calling')
    call_list = cursor.fetchall()
    conn.close()
    return render_template('profile.html', login = login, call_list = call_list)


@app.route('/logout', methods=['GET', 'POST']) # Функция для завершения сессии
def get_logout():
    session.pop('login', None)
    return redirect(url_for('get_home'))


@app.route('/create_post', methods = ['GET', 'POST']) # Создание поста с услугой
def get_create_post():
    if request.method == 'POST':
        if 'login' not in session:
            return redirect(url_for('get_log'))
        else:
            title = request.form['title']
            description = request.form['description']
            price = request.form['price']
            file = request.files['photo']

            if file:
                filename = file.filename

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)


                conn = sqlite3.connect('post.db')
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO post (title, description, price, file_path) 
                VALUES (?, ?, ?, ?)''',
                (title, description, price, file_path))


                conn.commit()
                conn.close()

            return redirect(url_for('get_home'))
    return render_template('create_post.html')


@app.route('/post<int:id>', methods = ['GET','POST']) # Страница с подробным окном услуги
def get_details(id):
    conn = sqlite3.connect('post.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM post WHERE id = ?', (id,))
    post = cursor.fetchone()

    conn.close()
    return render_template('post.html', post = post)


@app.route('/search', methods=['GET', 'POST']) # Поиск среди услуг по ключевому слову
def get_search():
    conn = sqlite3.connect('post.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM post')
    posts = cursor.fetchall()


    final = []
    search = request.form.get('search')

    if search:
        search = search.lower()

        for i in range(len(posts)):
            if search in posts[i][1] or search in posts[i][2]:
                final.append(posts[i])
            else:
                continue
            conn.close()
    return render_template('home.html', spisok = final)


@app.route('/calling', methods = ['GET','POST']) # Страница оформления заявки на вызов
def get_calling():
    if 'login' not in session:
        return redirect(url_for('get_log'))
    else:
        conn = sqlite3.connect('post.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM post')
        posts = cursor.fetchall()
        conn.close()

        if request.method == 'POST':
            doctor = request.form.get('doctor')
            day = request.form.get('day')
            time = request.form.get('time')

            if doctor and day and time:
                conn = sqlite3.connect('calling.db')
                cursor = conn.cursor()
                cursor.execute('''
                        INSERT INTO calling (doctor, day, time) 
                        VALUES (?, ?, ?)''',
                        (doctor, day, time))
                conn.commit()
                conn.close()

            return redirect(url_for('get_profile'))
    return render_template('calling.html', posts = posts)


@app.route('/up', methods=['GET', 'POST']) # Сортировака по возрастанию
def get_up():
    conn = sqlite3.connect('post.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM post ORDER BY price')
    posts = cursor.fetchall()

    conn.close()
    return render_template('home.html', spisok = posts)


@app.route('/down', methods = ['GET', 'POST']) # Сортировака по убыванию
def get_down():
    conn = sqlite3.connect('post.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM post ORDER BY price DESC')
    posts = cursor.fetchall()

    conn.close()
    return render_template('home.html', spisok = posts)


@app.route('/redact/<int:id>', methods=['GET','POST']) # Страница для редактирования услуг
def get_redact(id):
    conn = sqlite3.connect('post.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM post WHERE id = ?', (id,))
    post = cursor.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        file = request.files['photo']

        if file and file.filename:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            cursor.execute('''
                UPDATE post SET title = ?, description = ?, price = ?, file_path = ? WHERE id = ?''',
                (title, description, price, file_path, id))
        
        else:
            cursor.execute('''
                UPDATE post SET title = ?, description = ?, price = ? WHERE id = ?''',
                (title, description, price, id))

        conn.commit()
        conn.close()

        return redirect(url_for('get_details', id=id))
    return render_template('redact.html', post = post)


if __name__ == '__main__':
    app.run(debug=True) # Запуск приложения