1. ```poetry install --no-root``` or ```python -m venv .venv pip install -r requirements.txt``` (check dependencies in pyproject.toml)
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
