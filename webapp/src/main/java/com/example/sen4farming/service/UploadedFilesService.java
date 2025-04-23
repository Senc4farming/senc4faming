package com.example.sen4farming.service;

import com.example.sen4farming.dto.EvalScriptDto;
import com.example.sen4farming.dto.GrupoTrabajoDto;
import com.example.sen4farming.dto.UploadedFilesDto;
import com.example.sen4farming.model.GrupoTrabajo;
import com.example.sen4farming.model.UploadedFiles;
import com.example.sen4farming.repository.GrupoRepository;
import com.example.sen4farming.repository.UploadedFilesRepository;
import com.example.sen4farming.service.mapper.GrupoMapper;
import com.example.sen4farming.service.mapper.UploadedFilesMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;


@Service
public class UploadedFilesService extends AbstractBusinessService<UploadedFiles,Integer, UploadedFilesDto,
        UploadedFilesRepository, UploadedFilesMapper>   {
    //


    //Acceso a los datos de la bbdd
    public UploadedFilesService(UploadedFilesRepository repo, UploadedFilesMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public UploadedFilesDto guardar(UploadedFilesDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final UploadedFiles entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        UploadedFiles entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<UploadedFilesDto> lDto){
        Iterator<UploadedFilesDto> it = lDto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            UploadedFiles grupo = getMapper().toEntity(it.next());
            getRepo().save(grupo);
        }
    }

    public Page<UploadedFilesDto> buscarTodosPorUsuarioId(PageRequest of, long id) {
        return this.getRepo().findUploadedFilesByUsuarioUpload_Id(of, id).map(this.getMapper()::toDto);
    }
}
