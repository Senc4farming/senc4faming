package com.example.sen4farming.web.controller;

import com.example.sen4farming.config.details.SuperCustomerUserDetails;
import com.example.sen4farming.config.websocket.OutputMessage;
import com.example.sen4farming.config.websocket.WebSocketMessage;
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

    @GetMapping("/websocket")
    public String mostrarwebsocket( ModelMap interfazConPantalla){

        String  userName = "no informado";
        System.out.println(SecurityContextHolder.getContext().getAuthentication().getPrincipal().toString());
        //Comprobamos si hay usuario logeado
        if (SecurityContextHolder.getContext().getAuthentication().getPrincipal().equals("anonymousUser")){
            userName = "anonimo@anonimo";
        }
        else {
            userName = ((SuperCustomerUserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        }

        interfazConPantalla.addAttribute("userName", userName);
        return "websocket/websocket";
    }

    @MessageMapping("/chat")
    @SendTo("/topic/messages")
    public OutputMessage send(WebSocketMessage message) throws Exception {
        String time = new SimpleDateFormat("HH:mm").format(new Date());
        return new OutputMessage(message.getFrom(), message.getText(), time);
    }
}
