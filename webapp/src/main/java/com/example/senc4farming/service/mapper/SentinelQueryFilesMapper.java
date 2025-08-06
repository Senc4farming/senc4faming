package com.example.senc4farming.service.mapper;

import com.example.senc4farming.dto.SentinelQueryFilesDto;
import com.example.senc4farming.model.SentinelQueryFiles;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;
import com.example.senc4farming.util.DateFormat;

@NoArgsConstructor
@Service
public class SentinelQueryFilesMapper extends AbstractServiceMapper<SentinelQueryFiles, SentinelQueryFilesDto> {
    //Convertir de entidad a dtoç
    @Override
    public SentinelQueryFilesDto toDto(SentinelQueryFiles entidad){
        final SentinelQueryFilesDto dto = new SentinelQueryFilesDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        dto.setPublicationDate(DateFormat.parseDateZuluStr(entidad.getPublicationDate()));
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public SentinelQueryFiles toEntity(SentinelQueryFilesDto dto){
        final SentinelQueryFiles entidad = new SentinelQueryFiles();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }


}
