package com.example.jpa_formacion.service;


import com.example.jpa_formacion.dto.AyudaUsrDTO;
import com.example.jpa_formacion.model.AyudaUsr;
import com.example.jpa_formacion.repository.AyudaUsrRepository;
import com.example.jpa_formacion.repository.RoleRepository;
import com.example.jpa_formacion.repository.UsuarioRepository;
import com.example.jpa_formacion.service.mapper.AyudaUsrMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;



@Service
public class AyudaUsrService extends AbstractBusinessService<AyudaUsr, Integer, AyudaUsrDTO, AyudaUsrRepository,
        AyudaUsrMapper> {


    @Autowired
    protected AyudaUsrService(AyudaUsrRepository repository, AyudaUsrMapper serviceMapper,
                              UsuarioRepository usuarioRepository, RoleRepository roleRepository) {
        super(repository, serviceMapper);

    }


}
