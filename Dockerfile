FROM python:3
WORKDIR /app
COPY ./src/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY ./src/* ./
RUN chmod +x ./bathrooms/get_geo_location.py
CMD python ./bathrooms/get_geo_location.py
RUN chmod +x ./main.py
CMD python ./main.py
