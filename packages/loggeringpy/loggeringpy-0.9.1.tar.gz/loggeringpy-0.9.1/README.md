## Документация к модулю логирования
Модуль logger предоставляет функции для логирования действий в Python. Он позволяет создавать файл логов и записывать в него сообщения различных уровней, а также выводить эти сообщения в консоль.


![PyPI - Version](https://img.shields.io/pypi/v/dacite?style=flat&label=dacite)
![PyPI - Version](https://img.shields.io/pypi/v/colorama?style=flat&label=colorama)


## Подключение
Прежде чем использовать модуль, убедитесь, что у вас установлен Python версии 3.x и выше.
```python
import loggeringpy
```
## Функции модуля
# 1. Создание файла для логирования:
Создает файл логов с указанным именем. Если файл уже существует, он будет дописыватся
Убедитесь, что у вас имеются права на запись в директорию, где вы хотите создать файл логов.
 ```python
create_file(name, location, type, writing)
```
Параметры:

name -> Имя файла для логирования


location -> путь до директории файла логов


type -> тип выходного файла. txt либо log


writing - Будут ли логи записыватся в файл. True - да, False - нет

# Пример:
```python
import loggeringpy

logger.create_file("log", "./assets", ".log", True)
```
Output:


![image](https://github.com/user-attachments/assets/46ca7094-5031-45cf-b1d9-e2c61175dabd)



## 2. Уровень логирования INFO и его функция:

Выводит в консоль лог с уровнем INFO и записывает его в файл.


```python
logger.info(text)
```
Параметры:


text -> Текст который будет выведен в консоль и записан в файл





Пример:
```python
import loggeringpy

logger.create_file("log", "./assets", ".log", True)
logger.info("Test, check file and console")
```
Output:


![image](https://github.com/user-attachments/assets/8b97093e-06a2-4918-bd97-0e18875a2494)


## 3. Уровень логирования WARN и его функция:


Выводит в консоль лог с уровнем warning и записывает его в файл.

```python
logger.warning(text)
```
Параметры:


text -> Текст который будет выведен в консоль и записан в файл

Пример:


```python
import loggeringpy

logger.create_file("log", "./assets", ".log", True)
logger.warning("Test, check file and console")
```
Output:


![image](https://github.com/user-attachments/assets/812c10a8-4e28-43c9-99c4-e02fce24c9d5)


## 4. Уровень логирования SUCCESS и его функция:
Выводит в консоль лог с уровнем success и записывает его в файл.

```python
logger.success(text)
```
Параметры:


text -> Текст который будет выведен в консоль и записан в файл

Пример:


```python
import loggeringpy

logger.create_file("log", "./assets", ".log", True)
logger.success("Test, check file and console")
```
Output:

![image](https://github.com/user-attachments/assets/0e103fe1-865b-4427-aad1-df8b5d3446a8)


## 5. Уровень логирования CRIT и его функция:
Выводит в консоль лог с уровнем critical и записывает его в файл.

```python
logger.critical(text)
```
Параметры:


text -> Текст который будет выведен в консоль и записан в файл

Пример:


```python
import loggeringpy

logger.create_file("log", "./assets", ".log", True)
logger.critical("Test, check file and console")
```
Output:

![image](https://github.com/user-attachments/assets/4ea60f10-8b9f-4356-bbc3-fa5a2d00a41d)



## 6. Уровень логирования DEBUG и его функция:
Выводит в консоль лог с уровнем debug и записывает его в файл.


```python
logger.debug(text)
```
Параметры:


text -> Текст который будет выведен в консоль и записан в файл

Пример:


```python
import loggeringpy

logger.create_file("log", "./assets", ".log", True)
logger.debug("Test, check file and console")
```
Output:

![image](https://github.com/user-attachments/assets/04b52fc7-f25e-4683-9ed7-636aa2dca637)
