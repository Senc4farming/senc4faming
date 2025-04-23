package com.example.sen4farming.service.mapper;


import com.example.sen4farming.dto.AyudaUsrDTO;
import com.example.sen4farming.dto.MenuDTO;
import com.example.sen4farming.model.AyudaUsr;
import com.example.sen4farming.model.Menu;
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.stream.Collectors;

@Service
public class AyudaUsrMapper extends AbstractServiceMapper<AyudaUsr, AyudaUsrDTO> {

    @Autowired
    public AyudaUsrMapper(RoleServiceMapper roleServiceMapper) {
    }

    @Override
    public AyudaUsr toEntity(AyudaUsrDTO dto) throws Exception {
        final AyudaUsr entidad = new AyudaUsr();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return entidad;
    }

    @Override
    public AyudaUsrDTO toDto(AyudaUsr entidad) {
        final AyudaUsrDTO dto = new AyudaUsrDTO();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }

}
