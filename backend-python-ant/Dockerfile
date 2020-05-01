FROM python:3.7-slim
RUN pip install --upgrade pip && pip install pipenv
WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install
COPY . .
ENTRYPOINT ["pipenv", "run", "python", "server.py"]
EXPOSE 80
