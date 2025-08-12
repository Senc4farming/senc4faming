package com.example.senc4farming.model;


import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.io.Serializable;
import java.util.Set;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "role")
public class Role implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String roleName;

    @Column(nullable = false)
    private Integer showOnCreate;

    @Column(nullable = false)
    private String roleNameEn;
    @Column(nullable = false)
    private String roleNameEs;
    @Column(nullable = false)
    private String roleNameFr;
    @Column(nullable = false)
    private String roleName_01;
    @Column(nullable = false)
    private String roleName_02;
    @Column(nullable = false)
    private String roleName_03;
    @Column(nullable = false)
    private String roleName_04;
    @ManyToMany(fetch = FetchType.EAGER, mappedBy = "roles")
        private Set<Usuario>  usuarios;

}
