package com.example.sen4farming.service;

import com.example.sen4farming.dto.DatosLucas2018Dto;
import com.example.sen4farming.dto.DatosUploadCsvDto;
import com.example.sen4farming.model.DatosLucas2018;
import com.example.sen4farming.model.DatosUploadCsv;
import com.example.sen4farming.repository.DatosLucas2018Repository;
import com.example.sen4farming.repository.DatosUploadCsvRepository;
import com.example.sen4farming.service.mapper.DatosLucas2018Mapper;
import com.example.sen4farming.service.mapper.DatosUploadCsvMapper;
import org.springframework.stereotype.Service;

import java.util.Iterator;
import java.util.List;


@Service
public class DatosUploadCsvService extends AbstractBusinessService<DatosUploadCsv,Long, DatosUploadCsvDto,
        DatosUploadCsvRepository, DatosUploadCsvMapper>   {
    //


    //Acceso a los datos de la bbdd
    public DatosUploadCsvService(DatosUploadCsvRepository repo, DatosUploadCsvMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public DatosUploadCsvDto guardar(DatosUploadCsvDto dto){
        //Traduzco del dto con datos de entrada a la entidad
        final DatosUploadCsv entidad = getMapper().toEntity(dto);
        //Guardo el la base de datos
        DatosUploadCsv entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }

    //Método para guardar una lista de grupos
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<DatosUploadCsvDto> ldto){
        Iterator<DatosUploadCsvDto> it = ldto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            DatosUploadCsv ent = getMapper().toEntity(it.next());
            getRepo().save(ent);
        }
    }
    public List<DatosUploadCsvDto> getUploadedCsvData (Integer id,  String str){
        return  getMapper().toDto(getRepo().findBySearchidAndAndPath(id, str));

    }
    public List<DatosUploadCsvDto> getUploadedCsvDataSearchId (Integer id){
        return  getMapper().toDto(getRepo().findBySearchid(id));

    }
    public DatosUploadCsv getlucasreglike(Integer id ,String pointid,  String band , String str){
        return getRepo().findBySearchidAndPointidAndBandAndPathLike(id,pointid, band, str);
    }

}
