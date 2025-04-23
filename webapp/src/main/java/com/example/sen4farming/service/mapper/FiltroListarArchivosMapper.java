package com.example.sen4farming.service.mapper;

import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.FiltroListarArchivosDto;
import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.FiltroListarArchivos;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@Service
public class FiltroListarArchivosMapper extends AbstractServiceMapper<FiltroListarArchivos, FiltroListarArchivosDto> {
    //Convertir de entidad a dtoç
    @Override
    public FiltroListarArchivosDto toDto(FiltroListarArchivos entidad){
        final FiltroListarArchivosDto dto = new FiltroListarArchivosDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public FiltroListarArchivos toEntity(FiltroListarArchivosDto dto){
        final FiltroListarArchivos entidad = new FiltroListarArchivos();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }

    public FiltroListarArchivosMapper() {
    }
}
