package com.example.senc4farming.service.websockets;

import com.example.senc4farming.dto.websockets.MensajeDto;
import com.example.senc4farming.model.Mensaje;

import com.example.senc4farming.model.websockets.Notificacion;
import com.example.senc4farming.model.websockets.PrivateMessage;
import com.example.senc4farming.repository.MensajeRepositorio;
import com.example.senc4farming.repository.NotificacionRepositorio;
import com.example.senc4farming.service.AbstractBusinessService;
import com.example.senc4farming.service.mapper.MensajeMapper;
import lombok.extern.log4j.Log4j2;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.MessageHeaders;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.SimpMessageType;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;


@Service
@Log4j2
public class MessagingService extends AbstractBusinessService<Mensaje,Integer, MensajeDto,
        MensajeRepositorio, MensajeMapper> {


    private final  NotificacionRepositorio notificacionRepositorio;


    SimpMessagingTemplate simpMessagingTemplate;

    protected MessagingService(MensajeRepositorio mensajeRepositorio, MensajeMapper mapper, NotificacionRepositorio notificacionRepositorio) {
        super(mensajeRepositorio, mapper);
        this.notificacionRepositorio = notificacionRepositorio;
    }

    public void enviarMensajeSTOMPDeNotificacion(PrivateMessage message, Notificacion notificacion)
    {
        simpMessagingTemplate.convertAndSendToUser(
                message.getTo(),
                "/specific",
                message,
                createHeaders(message.getTo(),
                        String.valueOf(notificacion.getId()))
        );
        log.info("Mensaje enviado a: " + message.getTo());
    }


    public Notificacion crearNotificacion(String userTo, String userFrom, String mensaje)  {

        Notificacion notificacion = new Notificacion();
        notificacion.setEstado("Pendiente");
        notificacion.setFecha(LocalDateTime.now());
        notificacion.setUserTo(userTo);
        notificacion.setUserFrom(userFrom);
        notificacion.setText(mensaje);
        notificacionRepositorio.save(notificacion);
        return notificacion;

    }
    /**
     * Envía un mensaje privado a través de la cola de mensajes STOMP.
     *
     * @param privateMessage El mensaje privado a enviar.
     */
    public void enviarMensajePrivado(PrivateMessage privateMessage) {
        simpMessagingTemplate.convertAndSendToUser(
                privateMessage.getTo(),
                "/specific",
                privateMessage,
                createHeaders(privateMessage.getTo(), String.valueOf(privateMessage.getNotificationID()))
        );
        log.info("Mensaje enviado a: " + privateMessage.getTo());
    }


    /**
     * Crea los encabezados del mensaje con el destinatario y el ID de notificación.
     *
     * @param recipient     El destinatario del mensaje.
     * @param notificationID El ID de la notificación.
     * @return Los encabezados del mensaje.
     */
    public MessageHeaders createHeaders(String recipient, String notificationID) {
        SimpMessageHeaderAccessor headerAccessor = SimpMessageHeaderAccessor.create(SimpMessageType.MESSAGE);
        headerAccessor.addNativeHeader("notificationID", notificationID);
        return headerAccessor.getMessageHeaders();
    }




}


