package com.example.sen4farming.service;

import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.EvalScriptLaunchDto;
import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.EvalScriptLaunch;
import com.example.sen4farming.repository.EvalScriptLaunchRepository;
import com.example.sen4farming.repository.EvalScriptRepository;
import com.example.sen4farming.service.mapper.EvalScriptLaunchMapper;
import com.example.sen4farming.service.mapper.EvalScriptMapper;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;


@Service
public class EvalScriptLaunchService extends AbstractBusinessService<EvalScriptLaunch,Integer, EvalScriptLaunchDto,
        EvalScriptLaunchRepository, EvalScriptLaunchMapper>   {
    //


    //Acceso a los datos de la bbdd
    public EvalScriptLaunchService(EvalScriptLaunchRepository repo, EvalScriptLaunchMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public EvalScriptLaunchDto guardar(EvalScriptLaunchDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final EvalScriptLaunch entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        EvalScriptLaunch entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<EvalScriptLaunchDto> ldto){
        Iterator<EvalScriptLaunchDto> it = ldto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            EvalScriptLaunch ent = getMapper().toEntity(it.next());
            getRepo().save(ent);
        }
    }


}
