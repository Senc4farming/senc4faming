package com.example.senc4farming.service.mapper;

import com.example.senc4farming.dto.SentinelQueryFilesTiffDto;
import com.example.senc4farming.model.SentinelQueryFilesTiff;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
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

}
