FROM maven:3-amazoncorretto-17

RUN /usr/sbin/groupadd nonroot \
    && /usr/sbin/groupadd docker \
    && adduser  nonroot -g nonroot \
    && usermod -aG docker   nonroot

USER nonroot

WORKDIR /webapp
COPY .. .
RUN mvn clean install
CMD mvn spring-boot:run