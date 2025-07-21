package com.example.jpa_formacion.service;

import com.example.jpa_formacion.dto.RoleDTO;
import com.example.jpa_formacion.model.Role;
import com.example.jpa_formacion.repository.RoleRepository;
import com.example.jpa_formacion.repository.UsuarioRepository;
import com.example.jpa_formacion.service.mapper.RoleServiceMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RoleService extends AbstractBusinessService<Role, Long, RoleDTO, RoleRepository, RoleServiceMapper> {



    protected RoleService(RoleRepository repository, RoleServiceMapper serviceMapper) {
        super(repository, serviceMapper);
    }

    public List<RoleDTO> buscarTodosAlta(){
        return  this.getMapper().toDto(this.getRepo().findAllByShowOnCreate(1));
    }

}
