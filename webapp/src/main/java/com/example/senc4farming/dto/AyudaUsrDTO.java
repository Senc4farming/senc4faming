package com.example.senc4farming.dto;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.io.Serializable;


@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AyudaUsrDTO implements Serializable {
    private Integer id;
    private String url;
    private String title;
    private String description;
    private String body;



}
