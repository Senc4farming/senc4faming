package com.example.jpa_formacion.model.websockets;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor

public class PrivateMessage {

    private String notificationID;

    private String text;

    private String to;

    private String from;


}
