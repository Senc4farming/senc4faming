package com.example.senc4farming.controller;

import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.config.websocket.OutputMessage;
import com.example.senc4farming.config.websocket.WebSocketMessage;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.GetMapping;

import java.text.SimpleDateFormat;
import java.util.Date;

@Controller
public class AppWebSocketController {
    Logger logger = LogManager.getLogger(this.getClass());

    @GetMapping("/websocket")
    public String mostrarwebsocket( ModelMap interfazConPantalla){

        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            interfazConPantalla.addAttribute("userName", "anonimo@anonimo");
        }
        else {
            interfazConPantalla.addAttribute("userName",
             ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).
                     getUsername());
        }


        return "websocket/websocket";
    }

    @MessageMapping("/chat")
    @SendTo("/topic/messages")
    public OutputMessage send(WebSocketMessage message)  {
        String time = new SimpleDateFormat("HH:mm").format(new Date());
        return new OutputMessage(message.getFrom(), message.getText(), time);
    }
}
