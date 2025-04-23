package com.example.sen4farming.service;

import com.example.sen4farming.dto.FiltroConsultaKalmanDto;
import com.example.sen4farming.dto.FiltroListarArchivosDto;
import com.example.sen4farming.model.FiltroConsultaKalman;
import com.example.sen4farming.model.FiltroListarArchivos;
import com.example.sen4farming.repository.FiltroConsultaKalmanRepository;
import com.example.sen4farming.repository.FiltroListarArchivosRepository;
import com.example.sen4farming.service.mapper.FiltroConsultaKalmanMapper;
import com.example.sen4farming.service.mapper.FiltroListarArchivosMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;


@Service
public class FiltroConsultaKalmanService extends AbstractBusinessService<FiltroConsultaKalman,Integer, FiltroConsultaKalmanDto,
        FiltroConsultaKalmanRepository, FiltroConsultaKalmanMapper>   {
    //


    //Acceso a los datos de la bbdd
    public FiltroConsultaKalmanService(FiltroConsultaKalmanRepository repo, FiltroConsultaKalmanMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public FiltroConsultaKalmanDto guardar(FiltroConsultaKalmanDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final FiltroConsultaKalman entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        FiltroConsultaKalman entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<FiltroConsultaKalmanDto> ldto){
        Iterator<FiltroConsultaKalmanDto> it = ldto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            FiltroConsultaKalman ent = getMapper().toEntity(it.next());
            getRepo().save(ent);
        }
    }

    public Page<FiltroConsultaKalmanDto> buscarTodosPorUsuarioId(PageRequest of, long id) {
        return this.getRepo().findFiltroConsultaKalmanByUserid(of, id).map(this.getMapper()::toDto);
    }
}
