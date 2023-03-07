FROM python
WORKDIR /app
COPY req.txt /app
RUN python -m pip install -r req.txt

COPY . /app
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:application"]

