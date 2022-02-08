FROM fedora

RUN curl https://download-ib01.fedoraproject.org/pub/fedora/linux/releases/34/Everything/x86_64/os/Packages/p/pdf2svg-0.2.3-13.fc34.x86_64.rpm --output pdf2svg.rpm
RUN dnf -y install cairo
RUN dnf -y install poppler-glib
RUN rpm -i pdf2svg.rpm
RUN rm pdf2svg.rpm

RUN dnf -y install texlive-scheme-basic
RUN dnf -y install 'tex(standalone.cls)'
RUN dnf -y install python3
run dnf -y install python3-pip

RUN mkdir /app

COPY . /app/

WORKDIR /app

# api requirement
RUN python3 -m pip install flask numpy networkx

EXPOSE 5000

ARG PORT=5000

CMD ["python3","api.py"]
