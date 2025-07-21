package com.example.jpa_formacion.dto.websockets;

import com.example.jpa_formacion.model.Usuario;
import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.format.annotation.DateTimeFormat;

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
