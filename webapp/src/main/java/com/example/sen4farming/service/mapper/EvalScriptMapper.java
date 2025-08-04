package com.example.sen4farming.service.mapper;

import com.example.jpa_formacion.dto.EvalScriptDto;
import com.example.jpa_formacion.model.EvalScript;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
@Service
public class EvalScriptMapper extends AbstractServiceMapper<EvalScript, EvalScriptDto> {
    //Convertir de entidad a dtoç
    @Override
    public EvalScriptDto toDto(EvalScript entidad) {
        final EvalScriptDto dto = new EvalScriptDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad, dto);
        return dto;
    }

    //Convertir de dto a entidad
    @Override
    public EvalScript toEntity(EvalScriptDto dto) {
        final EvalScript entidad = new EvalScript();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto, entidad);
        return entidad;
    }

}
