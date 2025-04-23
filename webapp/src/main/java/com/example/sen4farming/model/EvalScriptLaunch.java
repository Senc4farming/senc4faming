package com.example.sen4farming.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "evalscriptlaunch")
public class EvalScriptLaunch {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    @Column(nullable = false)
    private String dateIni;
    @Column(nullable = false)
    private String dateFin;
    @Column(nullable = false)
    private String polygon;
    @Column(nullable = false)
    private String collection;
    @Column(nullable = false)
    private Integer resolution;
    @Column(precision=8, scale=2)
    private  BigDecimal ofsset;
    @Column(nullable = false)
    private Integer maxcloudcoverage;
    @Column(nullable = true)
    private String pathtiff;
    @Column(nullable = true)
    private String pathjson;



    @ManyToOne (fetch = FetchType.EAGER)
    @JoinColumn(name = "evalscript_id")
    private EvalScript evalScript;

}
