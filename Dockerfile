FROM resin/raspberry-pi2-python
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN git clone https://github.com/mjg59/python-broadlink.git
ADD server.py /server.py
ADD settings.ini /settings.ini
ADD settings.py /settings.py
CMD python server.py