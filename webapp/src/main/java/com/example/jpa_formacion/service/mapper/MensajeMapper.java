package com.example.jpa_formacion.service.mapper;

import com.example.jpa_formacion.dto.EvalScriptDto;
import com.example.jpa_formacion.dto.websockets.MensajeDto;
import com.example.jpa_formacion.model.EvalScript;
import com.example.jpa_formacion.model.Mensaje;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

@NoArgsConstructor
@Service
public class MensajeMapper extends AbstractServiceMapper<Mensaje, MensajeDto> {
    //Convertir de entidad a dtoç
    @Override
    public MensajeDto toDto(Mensaje entidad) {
        final MensajeDto dto = new MensajeDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad, dto);
        return dto;
    }

    //Convertir de dto a entidad
    @Override
    public Mensaje toEntity(MensajeDto dto) {
        final Mensaje entidad = new Mensaje();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto, entidad);
        return entidad;
    }

}
