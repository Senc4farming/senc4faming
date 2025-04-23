package com.example.sen4farming.service.mapper;

import com.example.sen4farming.dto.FiltroConsultaKalmanDto;
import com.example.sen4farming.dto.FiltroListarArchivosDto;
import com.example.sen4farming.model.FiltroConsultaKalman;
import com.example.sen4farming.model.FiltroListarArchivos;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@Service
public class FiltroConsultaKalmanMapper extends AbstractServiceMapper<FiltroConsultaKalman, FiltroConsultaKalmanDto> {
    //Convertir de entidad a dtoç
    @Override
    public FiltroConsultaKalmanDto toDto(FiltroConsultaKalman entidad){
        final FiltroConsultaKalmanDto dto = new FiltroConsultaKalmanDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad,dto);
        return dto;
    }
    //Convertir de dto a entidad
    @Override
    public FiltroConsultaKalman toEntity(FiltroConsultaKalmanDto dto){
        final FiltroConsultaKalman entidad = new FiltroConsultaKalman();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto,entidad);
        return entidad;
    }

    public FiltroConsultaKalmanMapper() {
    }
}
