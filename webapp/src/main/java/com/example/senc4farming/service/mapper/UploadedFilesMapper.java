package com.example.senc4farming.service.mapper;

import com.example.senc4farming.dto.UploadedFilesDto;
import com.example.senc4farming.model.UploadedFiles;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
@Service
public class UploadedFilesMapper extends AbstractServiceMapper<UploadedFiles, UploadedFilesDto> {
    //Convertir de entidad a dtoç
    @Override
    public UploadedFilesDto toDto(UploadedFiles entidad){
        final UploadedFilesDto dto = new UploadedFilesDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public UploadedFiles toEntity(UploadedFilesDto dto){
        final UploadedFiles entidad = new UploadedFiles();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }
}
