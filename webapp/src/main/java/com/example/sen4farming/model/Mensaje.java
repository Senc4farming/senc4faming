package com.example.sen4farming.model;

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
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "Mensaje")
public class Mensaje {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)

    private Integer id;

    @DateTimeFormat(pattern = "yyyy-MM-dd")
    @JsonFormat(pattern="yyyy-MM-dd")
    private LocalDate fechaEnvio;
    private String texto;
    private Boolean leido;
    private Boolean eliminar;

    @JsonBackReference
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "emisor",nullable = false)
    private Usuario emisor;

    @JsonBackReference
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "receptor",nullable = false)
    private Usuario receptor;

}
