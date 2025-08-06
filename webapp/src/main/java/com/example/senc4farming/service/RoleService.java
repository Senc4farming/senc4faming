package com.example.senc4farming.service;

import com.example.senc4farming.dto.RoleDTO;
import com.example.senc4farming.model.Role;
import com.example.senc4farming.repository.RoleRepository;
import com.example.senc4farming.service.mapper.RoleServiceMapper;
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
