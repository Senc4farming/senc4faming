package com.example.senc4farming.dto;


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.io.Serializable;
import java.util.Set;
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class MenuDTO implements Serializable {
    private Integer id;
    private String description;
    private String descriptionEs;

    private String descriptionEn;

    private String descriptionFr;

    private String description01;

    private String description02;

    private String description03;

    private String description04;

    private MenuDTO parent;
    private Integer order;
    private Integer active;
    private String url;
    private Set<RoleDTO> roles;


}
