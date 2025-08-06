package com.example.senc4farming.dto.websockets;

import com.example.senc4farming.model.Usuario;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
public class MensajeDto {


    private Integer id;
    private LocalDate fechaEnvio;
    private String texto;
    private Boolean leido;
    private Boolean eliminar;

    private Usuario emisor;
    private Usuario receptor;

}
