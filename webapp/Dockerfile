FROM maven:3-amazoncorretto-21
WORKDIR /senc4farming
COPY .. .
RUN mvn clean install
CMD mvn spring-boot:run