package com.example.sen4farming.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class DatosUploadCsvSearchDto {

    private Integer id;
    private String dateIni;
    private String dateFin;
    private String polygon;
    private String dataset;

}
