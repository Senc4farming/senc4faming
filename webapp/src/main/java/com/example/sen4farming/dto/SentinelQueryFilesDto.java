package com.example.sen4farming.dto;

import com.example.jpa_formacion.model.FiltroListarArchivos;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class SentinelQueryFilesDto {
    private Integer id;
    private String sentinelId;
    private String name;
    private String online;
    private String publicationDate;
    private String footprint;
    private String geofootprint;
    private Integer nunberOfTiff;
    private FiltroListarArchivos filtroListarArchivos;
}
