package com.example.sen4farming.service;


import com.example.sen4farming.dto.AyudaUsrDTO;
import com.example.sen4farming.dto.MenuDTO;
import com.example.sen4farming.model.AyudaUsr;
import com.example.sen4farming.model.Menu;
import com.example.sen4farming.model.Role;
import com.example.sen4farming.model.Usuario;
import com.example.sen4farming.repository.AyudaUsrRepository;
import com.example.sen4farming.repository.MenuRepository;
import com.example.sen4farming.repository.RoleRepository;
import com.example.sen4farming.repository.UsuarioRepository;
import com.example.sen4farming.service.mapper.AyudaUsrMapper;
import com.example.sen4farming.service.mapper.MenuServiceMapper;
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
