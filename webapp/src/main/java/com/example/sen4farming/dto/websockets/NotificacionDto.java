package com.example.sen4farming.dto.websockets;

import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;


@Getter
@Setter
public class NotificacionDto {
    private String id;
    private String userTo;
    private String userFrom;
    private String text;
    private LocalDateTime fecha;
    private String estado;

}
