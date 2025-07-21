package com.example.jpa_formacion.service.mapper;

import com.example.jpa_formacion.dto.DatosUploadCsvDto;
import com.example.jpa_formacion.model.DatosUploadCsv;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;
@NoArgsConstructor
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

}
