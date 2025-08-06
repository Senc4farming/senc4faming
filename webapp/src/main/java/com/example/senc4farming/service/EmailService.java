package com.example.senc4farming.service;


import com.example.senc4farming.dto.Email;
import jakarta.mail.*;
import jakarta.mail.internet.InternetAddress;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;

import java.util.Properties;


@Service
@RequiredArgsConstructor
public class EmailService {

    private final Environment env;
    private Session session;

    Logger logger = LogManager.getLogger(this.getClass());

    // MAILTRAP es un servicio que simula un servidor de correo
    // y permite probar y depurar el envío de correos electrónicos
    // sin enviar correos electrónicos reales a los destinatarios.

    public void initSesion() {
        //provide Mailtrap's host address
        String host = "live.smtp.mailtrap.io";
        //configure Mailtrap's SMTP server details
        Properties props = new Properties();
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.starttls.enable", "true");
        props.put("mail.smtp.host", host);
        props.put("mail.smtp.port", "587");
        //create the Session object
        session = Session.getInstance(props,
                new jakarta.mail.Authenticator() {
                    protected PasswordAuthentication getPasswordAuthentication() {
                        return new PasswordAuthentication(env.getProperty("mailstrap.username"), env.getProperty("mailstrap.password"));
                    }
                });
    }


    public void sendMail(Email mail) throws MessagingException {

        initSesion();
        try {
            //create a MimeMessage object
            Message message = new MimeMessage(session);
            //set From email field
            logger.info(mail.getFrom());
            message.setFrom(new InternetAddress(mail.getFrom()));
            //set To email field
            logger.info(mail.getTo());
            message.setRecipient(Message.RecipientType.TO, new InternetAddress(mail.getTo()));
            //set email subject field
            logger.info(mail.getSubject());
            message.setSubject(mail.getSubject());
            //set the content of the email message
            logger.info(mail.getContent());
            message.setText(mail.getContent());
            //send the email message
            logger.info("sendMail antes de Transport; %s " , mail.getContent());
            Transport.send(message);
            logger.info("Email Message Sent Successfully");
        } catch (MessagingException e) {
            e.printStackTrace();
            throw e;
        }
    }
}


