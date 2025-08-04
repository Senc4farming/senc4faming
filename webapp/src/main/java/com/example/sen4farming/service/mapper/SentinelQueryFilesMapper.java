package com.example.sen4farming.service.mapper;

import com.example.jpa_formacion.dto.SentinelQueryFilesDto;
import com.example.jpa_formacion.model.SentinelQueryFiles;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;
import com.example.jpa_formacion.util.DateFormat;

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
