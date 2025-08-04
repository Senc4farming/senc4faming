package com.example.sen4farming.service.websockets;

import com.example.jpa_formacion.dto.websockets.MensajeDto;
import com.example.jpa_formacion.dto.websockets.NotificacionDto;
import com.example.jpa_formacion.model.Mensaje;
import com.example.jpa_formacion.model.websockets.Notificacion;
import com.example.jpa_formacion.repository.MensajeRepositorio;
import com.example.jpa_formacion.repository.NotificacionRepositorio;
import com.example.jpa_formacion.service.AbstractBusinessService;
import com.example.jpa_formacion.service.mapper.MensajeMapper;
import com.example.jpa_formacion.service.mapper.NotificacionMapper;
import lombok.extern.log4j.Log4j2;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
@Log4j2
public class NotificacionService extends AbstractBusinessService<Notificacion,Integer, NotificacionDto, NotificacionRepositorio, NotificacionMapper> {

    protected NotificacionService(NotificacionRepositorio notificacionRepositorio, NotificacionMapper mapper) {
        super(notificacionRepositorio, mapper);
    }

    public Page<NotificacionDto> buscarTodosEstado(Pageable pageable,String usuario, String estado){
        return  getRepo().findByUserToAndEstado(pageable,usuario,estado).map(this.getMapper()::toDto);
    }
}
