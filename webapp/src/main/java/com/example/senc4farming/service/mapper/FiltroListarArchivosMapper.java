package com.example.senc4farming.service.mapper;


import com.example.senc4farming.dto.FiltroListarArchivosDto;
import com.example.senc4farming.model.FiltroListarArchivos;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
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


}
