package com.example.sen4farming.dto;


import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
@Getter
@Setter
public class RoleDTO implements Serializable {
    private Long id;
    private String roleName;

    private String roleNameEn;
    private String roleNameEs;
    private String roleNameFr;
    private String roleName01;
    private String roleName02;
    private String roleName03;
    private String roleName04;
}
