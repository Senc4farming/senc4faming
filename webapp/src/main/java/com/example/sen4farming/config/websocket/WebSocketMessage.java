package com.example.sen4farming.config.websocket;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class WebSocketMessage {
    private String from;
    private String text;
}