package com.example.sen4farming.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class QuerySocDto {

    String Point_id;
    String fechaIni;
    String fechaFin;
    String longitude;
    String latitude;
    String cloudcover;
    String reference;
    String soc;


}
