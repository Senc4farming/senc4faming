package com.example.senc4farming.service.websockets;

import com.example.senc4farming.dto.websockets.NotificacionDto;
import com.example.senc4farming.model.websockets.Notificacion;
import com.example.senc4farming.repository.NotificacionRepositorio;
import com.example.senc4farming.service.AbstractBusinessService;
import com.example.senc4farming.service.mapper.NotificacionMapper;
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
