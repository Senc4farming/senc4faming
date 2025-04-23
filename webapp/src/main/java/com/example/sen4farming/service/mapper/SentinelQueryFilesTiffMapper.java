package com.example.sen4farming.service.mapper;

import com.example.sen4farming.dto.SentinelQueryFilesDto;
import com.example.sen4farming.dto.SentinelQueryFilesTiffDto;
import com.example.sen4farming.model.SentinelQueryFiles;
import com.example.sen4farming.model.SentinelQueryFilesTiff;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@Service
public class SentinelQueryFilesTiffMapper extends AbstractServiceMapper<SentinelQueryFilesTiff, SentinelQueryFilesTiffDto> {
    //Convertir de entidad a dtoç
    @Override
    public SentinelQueryFilesTiffDto toDto(SentinelQueryFilesTiff entidad){
        final SentinelQueryFilesTiffDto dto = new SentinelQueryFilesTiffDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public SentinelQueryFilesTiff toEntity(SentinelQueryFilesTiffDto dto){
        final SentinelQueryFilesTiff entidad = new SentinelQueryFilesTiff();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }

    public SentinelQueryFilesTiffMapper() {
    }
}
