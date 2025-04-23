package com.example.sen4farming.dto;

import jakarta.persistence.Column;
import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
import java.util.Set;

@Getter
@Setter
public class AyudaUsrDTO implements Serializable {
    private Integer id;
    private String url;
    private String title;
    private String description;
    private String body;

    public AyudaUsrDTO() {
    }


}
