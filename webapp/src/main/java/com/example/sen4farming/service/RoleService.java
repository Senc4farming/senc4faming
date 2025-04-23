package com.example.sen4farming.service;

import com.example.sen4farming.dto.RoleDTO;
import com.example.sen4farming.model.Role;
import com.example.sen4farming.repository.RoleRepository;
import com.example.sen4farming.repository.UsuarioRepository;
import com.example.sen4farming.service.mapper.RoleServiceMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RoleService extends AbstractBusinessService<Role, Long, RoleDTO, RoleRepository, RoleServiceMapper> {

    private final UsuarioRepository usuarioRepository;

    protected RoleService(RoleRepository repository, RoleServiceMapper serviceMapper, UsuarioRepository usuarioRepository) {
        super(repository, serviceMapper);
        this.usuarioRepository = usuarioRepository;
    }

    public List<RoleDTO> buscarTodosAlta(){
        return  this.getMapper().toDto(this.getRepo().findAllByShowOnCreate(1));
    }

}
