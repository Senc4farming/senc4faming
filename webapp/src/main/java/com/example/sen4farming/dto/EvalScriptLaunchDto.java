package com.example.sen4farming.dto;

import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.EvalScriptLaunch;
import com.example.sen4farming.model.Usuario;
import jakarta.persistence.Column;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class EvalScriptLaunchDto {

    private Integer id;
    private String dateIni;
    private String dateFin;
    private String polygon;
    private String collection;
    private Integer resolution;
    private BigDecimal ofsset;
    private Integer maxcloudcoverage;
    private String pathtiff;
    private String pathjson;
    private EvalScript evalScript;

}
