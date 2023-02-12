<h1>BestHotelsBot</h1>
Простой телеграмм-бот, с помощью которого можно получить информацию по отелям (аналог сайта hotels.com).

<h2>Stacks</h2>
Бот написан на Python 3.10. 
Для работы бота необходимо дополнительно установить библиотеки из файла <b>requirements.txt</b>. 

Для получения токена бота необходимо обратиться к [@BotFather](https://t.me/BotFather).

Бот использует API "rapidapi.com". Для работы с данным API необходимо зарегистрироваться на сайте и получить свой RAPID_API_KEY:
<pre>headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}</pre>

Для работы с БД используется ORM Peewee. [См.документацию](http://docs.peewee-orm.com/en/latest/) 

<h2>Installation</h2>
В отдельном каталоге создайте виртуальное окружение:

<code>python -m venv <путь к виртуальному окружению></code>

Теперь активируем виртуальное окружение:

<pre>$ source env/bin/activate
(env) $</pre>
Для Windows процесс активации будет отличаться (допустим, что виртуальное окружение создано в C:\src\source):

Через cmd:
<pre>C:\src\source\> env\Scripts\activate.bat</pre>

Либо в PowerShell:
<pre>PS C:\src\source\> env\Scripts\Activate.ps1</pre>

Скопируйте все содержимое репозитория.
Установите библиотеки из файла <code>requirements.txt</code>.

Файл <code>.env.template</code> переименуйте в <code>.env</code> и скопируйте в него свои данные.

Запустите файл <code>main.py</code>
