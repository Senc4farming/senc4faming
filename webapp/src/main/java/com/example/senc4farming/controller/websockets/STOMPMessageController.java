package com.example.senc4farming.controller.websockets;


import com.example.senc4farming.model.websockets.Notificacion;
import com.example.senc4farming.model.websockets.PrivateMessage;
import com.example.senc4farming.repository.NotificacionRepositorio;
import com.example.senc4farming.service.UsuarioServiceFacade;
import com.example.senc4farming.service.websockets.MessagingService;
import lombok.extern.log4j.Log4j2;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.MessageHeaders;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.SimpMessageType;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;

import java.util.Optional;


/**
 * The type Greeting controller.
 */
@Controller
@Log4j2
@EnableWebSocketMessageBroker
public class STOMPMessageController {

    /**
     * The Simp messaging template.
     */
    @Autowired
    SimpMessagingTemplate simpMessagingTemplate;
    @Autowired
    MessagingService messagingService;
    @Autowired
    NotificacionRepositorio notificacionRepositorio;

    private final  UsuarioServiceFacade service;

    Logger logger = LogManager.getLogger(this.getClass());

    public STOMPMessageController(UsuarioServiceFacade service) {
        this.service = service;
    }

    /**
     * El ID de sesión (también conocido como ID de conexión) se genera automáticamente cuando un cliente se conecta
     * al servidor de Spring WebSocket. Este ID de sesión se utiliza para identificar de manera única la conexión
     * de un cliente y se puede utilizar para enviar mensajes a clientes específicos.
     *
     * En Spring WebSocket, el ID de sesión se puede obtener a través del encabezado simpSessionId en un método
     * controlador de mensajes. Este encabezado se agrega automáticamente por Spring WebSocket y contiene
     * el ID de sesión del cliente que envió el mensaje.
     *
     * @param message the message
     */
    @MessageMapping("/private")
    public void sendToSpecificUser(@Payload PrivateMessage message) {
        log.info("Dentro de private", message.getTo() + ":"+ message.getFrom()+ ":" , message.getNotificationID());
        // Creo mi notificación en la base de datos para poder controlar el estado de los mensajes
        Notificacion notificacion = messagingService.crearNotificacion(message.getTo(), message.getFrom(), message.getText());
        // Cuando ya tenemos el ID de la notificación, lo informamos en nuestro objeto PrivateMessage creado ad-hoc
        message.setNotificationID(notificacion.getId());

        // Componemos un nuevo mensaje STOMP con nuestro PrivateMessage
        simpMessagingTemplate.convertAndSendToUser(
                message.getTo(),
                "/specific",
                message,
                createHeaders(message.getTo(),
                        String.valueOf(notificacion.getId()))
        );
        log.info("Mensaje enviado a: " + message.getTo());
        log.info("Notificación creada con ID: " + notificacion.getId());
    }

    private MessageHeaders createHeaders(String recipient, String notificationID) {
        SimpMessageHeaderAccessor headerAccessor = SimpMessageHeaderAccessor.create(SimpMessageType.MESSAGE);
        headerAccessor.addNativeHeader("notificationID",notificationID);
        return headerAccessor.getMessageHeaders();
    }


    @MessageMapping("/recibir")
    public void receiveMessage(@Payload PrivateMessage message) {

        String notificationId = message.getNotificationID();
        Optional<Notificacion> notificacion = notificacionRepositorio.findById(notificationId);

        if (notificacion.isPresent()) {
            notificacion.get().setEstado("READ");
            logger.info("Notificación {} marcada como recibida", notificationId);
            notificacionRepositorio.save(notificacion.get());
        } else {
            logger.error("No se encontró la notificación con ID: {}", notificationId);

        }
    }
}
