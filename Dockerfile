FROM python:3
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY ./* ./
RUN chmod +x ./main.py
CMD python ./main.py
