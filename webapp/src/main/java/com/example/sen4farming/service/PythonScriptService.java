package com.example.sen4farming.service;

import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.PythonScriptDto;
import com.example.sen4farming.model.EvalScript;
import com.example.sen4farming.model.PythonScript;
import com.example.sen4farming.repository.EvalScriptRepository;
import com.example.sen4farming.repository.PythonScriptRepository;
import com.example.sen4farming.service.mapper.EvalScriptMapper;
import com.example.sen4farming.service.mapper.PythonScriptMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;


@Service
public class PythonScriptService extends AbstractBusinessService<PythonScript,Integer, PythonScriptDto,
        PythonScriptRepository, PythonScriptMapper>   {
    //


    //Acceso a los datos de la bbdd
    public PythonScriptService(PythonScriptRepository repo, PythonScriptMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public PythonScriptDto guardar(PythonScriptDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final PythonScript entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        PythonScript entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<PythonScriptDto> ldto){
        Iterator<PythonScriptDto> it = ldto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            PythonScript ent = getMapper().toEntity(it.next());
            getRepo().save(ent);
        }
    }

    public Page<PythonScriptDto> buscarTodosPorUsuarioId(PageRequest of, Integer id) {
        return this.getRepo().findPythonScriptByUsuarioPythonScript_Id(of, id).map(this.getMapper()::toDto);
    }
}
