package com.example.sen4farming.dto;



import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class FiltroConsultaKalmanDto {
    private Integer id;
    private Integer csvid;
    private Integer pointid;
    private double offset;
    private long cloudCover;
    private Integer numberOfGeeImages;
    private String reference;
    private Integer userid;
    private Integer numDaysSerie;
    private String origin;
    private String satellite;
    private String kalmanpred;
    private String dirstr;
    private String path;

}
