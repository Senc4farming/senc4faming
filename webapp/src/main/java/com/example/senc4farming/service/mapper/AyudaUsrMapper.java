package com.example.senc4farming.service.mapper;


import com.example.senc4farming.dto.AyudaUsrDTO;
import com.example.senc4farming.model.AyudaUsr;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;


@NoArgsConstructor
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
