package com.example.sen4farming.service.mapper;

import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.GrupoTrabajoDto;
import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.GrupoTrabajo;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@Service
public class EvalScriptMapper extends AbstractServiceMapper<EvalScript, EvalScriptDto> {
    //Convertir de entidad a dtoç
    @Override
    public EvalScriptDto toDto(EvalScript entidad){
        final EvalScriptDto dto = new EvalScriptDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public EvalScript toEntity(EvalScriptDto dto){
        final EvalScript entidad = new EvalScript();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }

    public EvalScriptMapper() {
    }
}
