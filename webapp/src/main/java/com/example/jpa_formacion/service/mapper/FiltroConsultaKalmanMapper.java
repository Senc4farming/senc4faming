package com.example.jpa_formacion.service.mapper;

import com.example.jpa_formacion.dto.FiltroConsultaKalmanDto;
import com.example.jpa_formacion.model.FiltroConsultaKalman;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
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
}
