FROM python:3.10

RUN useradd -ms /bin/bash stenting
WORKDIR /home/stenting
USER stenting

COPY --chown=stenting . .
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
EXPOSE 8501
CMD ["venv/bin/streamlit", "run", "testv2.py"]

