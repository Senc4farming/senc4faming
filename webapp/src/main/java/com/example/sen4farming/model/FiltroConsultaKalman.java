package com.example.sen4farming.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "filtroconsultakalman")
public class FiltroConsultaKalman {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    @Column(nullable = false)
    private Integer csvid;
    @Column(nullable = true)
    private Integer pointid;
    @Column(nullable = true)
    private double offset;
    @Column(nullable = true)
    private long cloudCover;
    @Column(nullable = true)
    private Integer numberOfGeeImages;
    @Column(nullable = true)
    private String reference;
    @Column(nullable = true)
    private Integer userid;
    @Column(nullable = true)
    private Integer numDaysSerie;
    @Column(nullable = true)
    private String origin;
    @Column(nullable = true)
    private String satellite;
    @Column(nullable = true)
    private String kalmanpred;
    @Column(nullable = true)
    private String dirstr;
    @Column(nullable = true)
    private String path;

}
