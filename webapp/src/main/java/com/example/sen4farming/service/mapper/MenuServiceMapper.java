package com.example.sen4farming.service.mapper;


import com.example.sen4farming.dto.MenuDTO;
import com.example.sen4farming.model.Menu;
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.stream.Collectors;

@Service
public class MenuServiceMapper extends AbstractServiceMapper<Menu, MenuDTO> {

    private final RoleServiceMapper roleServiceMapper;

    @Autowired
    public MenuServiceMapper(RoleServiceMapper roleServiceMapper) {
        this.roleServiceMapper = roleServiceMapper;
    }

    @Override
    public Menu toEntity(MenuDTO dto) throws Exception {
        final Menu entidad = new Menu();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        entidad.setRoles(this.roleServiceMapper.toEntity(dto.getRoles().stream().collect(Collectors.toList())).stream()
                .collect(Collectors.toSet()));
        return entidad;
    }

    @Override
    public MenuDTO toDto(Menu entidad) {
        final MenuDTO dto = new MenuDTO();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        //dto.setRoles(this.roleServiceMapper.toDto(entidad.getRoles().stream().collect(Collectors.toList())).stream()
        //        .collect(Collectors.toSet()));
        return dto;
    }

}
