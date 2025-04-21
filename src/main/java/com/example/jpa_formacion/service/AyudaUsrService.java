package com.example.jpa_formacion.service;


import com.example.jpa_formacion.dto.AyudaUsrDTO;
import com.example.jpa_formacion.dto.MenuDTO;
import com.example.jpa_formacion.model.AyudaUsr;
import com.example.jpa_formacion.model.Menu;
import com.example.jpa_formacion.model.Role;
import com.example.jpa_formacion.model.Usuario;
import com.example.jpa_formacion.repository.AyudaUsrRepository;
import com.example.jpa_formacion.repository.MenuRepository;
import com.example.jpa_formacion.repository.RoleRepository;
import com.example.jpa_formacion.repository.UsuarioRepository;
import com.example.jpa_formacion.service.mapper.AyudaUsrMapper;
import com.example.jpa_formacion.service.mapper.MenuServiceMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.List;

@Service
public class AyudaUsrService extends AbstractBusinessService<AyudaUsr, Integer, AyudaUsrDTO, AyudaUsrRepository,
        AyudaUsrMapper> {


    @Autowired
    protected AyudaUsrService(AyudaUsrRepository repository, AyudaUsrMapper serviceMapper,
                              UsuarioRepository usuarioRepository, RoleRepository roleRepository) {
        super(repository, serviceMapper);

    }


}
