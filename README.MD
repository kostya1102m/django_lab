0. ```git clone https://github.com/kostya1102m/django_lab``` then switch to lab2 branch
1. ```poetry install``` or ```python -m venv .venv pip install -r requirements.txt``` (check dependencies in pyproject.toml)
2. create .env ( for instance:
    ```POSTGRES_USER=postgres```
    ```POSTGRES_PASSWORD=postgres```
    ```POSTGRES_DB=amazon_store```
    ```POSTGRES_PORT=5434```
    ```POSTGRES_HOST=localhost```
)
3. ```docker-compose up```
4. ```cd amazonstore```
5. ```python manage.py makemigrations store```
6. ```python manage.py migrate```
7. ```python manage.py extract_from_csv data/Amazon.csv```
8. ```python manage.py runserver```

NOTE: to check lab3 switch to lab3 branch