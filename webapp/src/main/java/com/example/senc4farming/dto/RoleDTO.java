package com.example.senc4farming.dto;


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
    private String roleName_01;
    private String roleName_02;
    private String roleName_03;
    private String roleName_04;
}
