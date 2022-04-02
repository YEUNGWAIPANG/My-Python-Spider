FROM python:3.8.3

ADD . .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

WORKDIR /Xinlangcaijing

CMD ["python3","/Xinlangcaijing/RunAllSpider.py"]
