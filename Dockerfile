FROM python:3.7-alpine
RUN apk add --no-cache gcc g++ make libffi-dev openssl-dev tzdata && \
  cp /usr/share/zoneinfo/Asia/Jerusalem /etc/localtime && \
  echo "Asia/Jerusalem" >  /etc/timezone
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["./run.sh"]
