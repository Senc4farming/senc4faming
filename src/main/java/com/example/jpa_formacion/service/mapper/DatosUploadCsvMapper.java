package com.example.jpa_formacion.service.mapper;

import com.example.jpa_formacion.dto.DatosLucas2018Dto;
import com.example.jpa_formacion.dto.DatosUploadCsvDto;
import com.example.jpa_formacion.model.DatosLucas2018;
import com.example.jpa_formacion.model.DatosUploadCsv;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@Service
public class DatosUploadCsvMapper extends AbstractServiceMapper<DatosUploadCsv, DatosUploadCsvDto> {
    //Convertir de entidad a dtoç
    @Override
    public DatosUploadCsvDto toDto(DatosUploadCsv entidad){
        final DatosUploadCsvDto dto = new DatosUploadCsvDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public DatosUploadCsv toEntity(DatosUploadCsvDto dto){
        final DatosUploadCsv entidad = new DatosUploadCsv();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }

    public DatosUploadCsvMapper() {
    }
}
