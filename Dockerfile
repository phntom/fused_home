FROM python:3.6-alpine
RUN apk add --no-cache gcc g++ make libffi-dev openssl-dev
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x run.sh
CMD ["./run.sh"]
