FROM maven:3-amazoncorretto-21

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

USER nonroot

ENTRYPOINT ["echo", "Welcome!"]

WORKDIR /webapp
COPY .. .
RUN mvn clean install
CMD ["mvn spring-boot:run"]