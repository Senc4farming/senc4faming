package com.example.senc4farming.service;


import com.example.senc4farming.dto.AyudaUsrDTO;
import com.example.senc4farming.model.AyudaUsr;
import com.example.senc4farming.repository.AyudaUsrRepository;
import com.example.senc4farming.repository.RoleRepository;
import com.example.senc4farming.repository.UsuarioRepository;
import com.example.senc4farming.service.mapper.AyudaUsrMapper;
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
