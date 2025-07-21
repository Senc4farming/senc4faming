package com.example.jpa_formacion.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;



@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class QuerySocDto {

    String pointId;
    String fechaIni;
    String fechaFin;
    String longitude;
    String latitude;
    String cloudcover;
    String reference;
    String soc;


}
