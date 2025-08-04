package com.example.sen4farming.service.mapper;


import com.example.jpa_formacion.dto.websockets.NotificacionDto;
import com.example.jpa_formacion.model.websockets.Notificacion;
import lombok.NoArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;



@NoArgsConstructor
@Service
public class NotificacionMapper extends AbstractServiceMapper<Notificacion, NotificacionDto> {
    //Convertir de entidad a dtoç
    @Override
    public NotificacionDto toDto(Notificacion entidad) {
        final NotificacionDto dto = new NotificacionDto();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(entidad, dto);
        return dto;
    }

    //Convertir de dto a entidad
    @Override
    public Notificacion toEntity(NotificacionDto dto) {
        final Notificacion entidad = new Notificacion();
        ModelMapper modelMapper = new ModelMapper();
        modelMapper.map(dto, entidad);
        return entidad;
    }

}
