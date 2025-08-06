package com.example.senc4farming.service;

import lombok.Getter;
import lombok.Setter;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
@Getter
@Setter
@Service
public class UsuarioServiceFacade {
    private final  UsuarioService service;
    private final RoleService roleService;

    private final GrupoService grupoService;

    private final PythonScriptService pythonScriptService;


    private final EmailService emailService;

    private  final BCryptPasswordEncoder  passwordEncoder;

    public UsuarioServiceFacade(UsuarioService service, RoleService roleService, GrupoService grupoService, PythonScriptService pythonScriptService, EmailService emailService, BCryptPasswordEncoder passwordEncoder) {
        this.service = service;
        this.roleService = roleService;
        this.grupoService = grupoService;
        this.pythonScriptService = pythonScriptService;
        this.emailService = emailService;
        this.passwordEncoder = passwordEncoder;
    }

    //Crea métodos para obtener dtos con datos de varias entidades


}
