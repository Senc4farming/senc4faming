package com.example.sen4farming.dto;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class UploadedFilesContentDto {
    private String depth;
    private String pointid;
    private String soc;
    private String latitude;
    private String longitude;
    private String surveydate;
    private String elev;
    private String desc1;
    private String desc2;
    private String desc3;

}
