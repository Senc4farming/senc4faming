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
@Table(name = "datosuploadcsv")
public class DatosUploadCsv {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column
    private Integer searchid;
    @Column
    private Integer keyapi;
    @Column
    private String longitud ;
    @Column
    private String latitud ;
    @Column
    private String pointid;
    @Column
    private String path;
    @Column
    private String userid;
    @Column
    private String reflectance;
    @Column
    private String band;
    @Column
    private String survey_date;
    @Column
    private String oc;
}
