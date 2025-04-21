package com.example.jpa_formacion.config.websocket;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class WebSocketMessage {
    private String from;
    private String text;
}