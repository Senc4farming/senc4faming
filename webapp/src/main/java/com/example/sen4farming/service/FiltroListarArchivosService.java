package com.example.sen4farming.service;

import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.FiltroListarArchivosDto;
import com.example.sen4farming.dto.SentinelQueryFilesDto;
import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.FiltroListarArchivos;
import com.example.sen4farming.repository.EvalScriptRepository;
import com.example.sen4farming.repository.FiltroListarArchivosRepository;
import com.example.sen4farming.service.mapper.EvalScriptMapper;
import com.example.sen4farming.service.mapper.FiltroListarArchivosMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;


@Service
public class FiltroListarArchivosService extends AbstractBusinessService<FiltroListarArchivos,Integer, FiltroListarArchivosDto,
        FiltroListarArchivosRepository, FiltroListarArchivosMapper>   {
    //


    //Acceso a los datos de la bbdd
    public FiltroListarArchivosService(FiltroListarArchivosRepository repo, FiltroListarArchivosMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public FiltroListarArchivosDto guardar(FiltroListarArchivosDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final FiltroListarArchivos entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        FiltroListarArchivos entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<FiltroListarArchivosDto> ldto){
        Iterator<FiltroListarArchivosDto> it = ldto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            FiltroListarArchivos ent = getMapper().toEntity(it.next());
            getRepo().save(ent);
        }
    }
    public Page<FiltroListarArchivosDto> buscarTodosPorFiltroId(PageRequest of, long id) {
        return this.getRepo().findFiltroListarArchivosByUsuarioFiltro_Id(of, id).map(this.getMapper()::toDto);
    }

}
