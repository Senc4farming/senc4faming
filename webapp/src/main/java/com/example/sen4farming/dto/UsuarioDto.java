package com.example.sen4farming.dto;

import com.example.sen4farming.model.GrupoTrabajo;
import com.example.sen4farming.model.Role;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.HashSet;
import java.util.Set;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class UsuarioDto {
    private long id;

    private String email;

    private String nombreUsuario;

    private String nombreEmail;

    private boolean active;

    private GrupoTrabajo grupoTrabajo;

    private Set<Role> roles = new HashSet<>();
}
