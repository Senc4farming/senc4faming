package com.example.jpa_formacion.dto;


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
    private String description_es;

    private String description_en;

    private String description_fr;

    private String description_01;

    private String description_02;

    private String description_03;

    private String description_04;

    private MenuDTO parent;
    private Integer order;
    private Integer active;
    private String url;
    private Set<RoleDTO> roles;


}
