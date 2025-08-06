package com.example.senc4farming.dto.websockets;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor

public class PrivateMessageDto {

    private String notificationID;

    private String text;

    private String to;

    private String from;
}
