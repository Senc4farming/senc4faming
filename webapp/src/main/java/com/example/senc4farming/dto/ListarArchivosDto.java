package com.example.senc4farming.dto;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;


@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class ListarArchivosDto {

    private String userName;

    private Long groupid;

    private Long  userid;

    private Integer  filterid;

    private String reference;

    private String dateIni;

    private String dateFin;

    private String polygon;

    private long cloudCover;

    private boolean removePrevData;
}
