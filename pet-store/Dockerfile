#use python 3.8
# FROM python:3.8-slim

# set working directory
WORKDIR /app

# copy requirements 
COPY requirements.txt .

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy all application files
COPY . .

# create images directory
RUN mkdir -p images

# use port 5001
EXPOSE 5001

# run the application
CMD ["python", "app.py"]
