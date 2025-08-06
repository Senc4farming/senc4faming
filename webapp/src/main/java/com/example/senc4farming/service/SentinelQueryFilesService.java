package com.example.senc4farming.service;

import com.example.senc4farming.apiitem.Listfiles;
import com.example.senc4farming.dto.SentinelQueryFilesDto;
import com.example.senc4farming.model.FiltroListarArchivos;
import com.example.senc4farming.model.SentinelQueryFiles;
import com.example.senc4farming.repository.SentinelQueryFilesRepository;
import com.example.senc4farming.service.mapper.SentinelQueryFilesMapper;
import jakarta.transaction.Transactional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;
import java.util.Optional;


@Service
@Transactional
public class SentinelQueryFilesService extends AbstractBusinessService<SentinelQueryFiles,Integer, SentinelQueryFilesDto,
        SentinelQueryFilesRepository, SentinelQueryFilesMapper>   {

    private final FiltroListarArchivosService filtroListarArchivosService;

    //Acceso a los datos de la bbdd
    public SentinelQueryFilesService(SentinelQueryFilesRepository repo, SentinelQueryFilesMapper serviceMapper
            , FiltroListarArchivosService filtroListarArchivosService) {

        super(repo, serviceMapper);
        this.filtroListarArchivosService = filtroListarArchivosService;
    }
    @Override
    public SentinelQueryFilesDto guardar(SentinelQueryFilesDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final SentinelQueryFiles entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        SentinelQueryFiles entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<SentinelQueryFilesDto> ldto){
        Iterator<SentinelQueryFilesDto> it = ldto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            SentinelQueryFiles ent = getMapper().toEntity(it.next());
            getRepo().save(ent);
        }
    }
    public void  deleteDesdeFiltro(Integer filtroid)  {

        this.getRepo().deleteSentinelQueryFilesByFiltroListarArchivos_Id(filtroid);
    }
    public void  guardarDesdeConsulta(List<Listfiles> dtos,Integer filtroid) {
        Iterator<Listfiles> it = dtos.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //
            Listfiles listfiles = it.next();
            SentinelQueryFiles ent = new SentinelQueryFiles();
            ent.setSentinelId(listfiles.getId());
            ent.setName(listfiles.getName());
            ent.setOnline(listfiles.getOnline());
            ent.setPublicationDate(listfiles.getPublicationDate());
            ent.setFootprint(listfiles.getFootprint());
            ent.setGeofootprint(listfiles.getGeofootprint());
            Optional<FiltroListarArchivos> filtroListarArchivos =
                    filtroListarArchivosService.buscar(filtroid);
            if (filtroListarArchivos.isPresent()) {
                ent.setFiltroListarArchivos(filtroListarArchivos.get());
            }
            this.getRepo().save(ent);
        }
    }


    public Page<SentinelQueryFilesDto> buscarTodosPorFiltroId(PageRequest of, long id) {
        return this.getRepo().findSentinelQueryFilesByFiltroListarArchivos_Id(of, id).map(this.getMapper()::toDto);
    }

}
