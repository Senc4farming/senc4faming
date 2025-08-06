package com.example.senc4farming.service;

import com.example.senc4farming.service.mapper.AbstractServiceMapper;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.*;

public abstract class AbstractBusinessService   <E, ID, DTO,  REPO extends JpaRepository<E,ID> ,
        MAPPER extends AbstractServiceMapper<E,DTO>>  {
    private final REPO repo;
    private final MAPPER serviceMapper;

    Logger logger = LogManager.getLogger(this.getClass());


    protected AbstractBusinessService(REPO repo, MAPPER mapper) {
        this.repo = repo;
        this.serviceMapper = mapper;
    }
    //Buscamos por id
    public Optional<E> buscar(ID id){return  this.repo.findById(id);}
    //Lista de todos los DTOs buscarTodos devolvera lista y paginas
    public List<DTO> buscarTodos(){
        logger.info("pepe");
        return  this.serviceMapper.toDto(this.repo.findAll());
    }

    public List<E> buscarEntidades(){
        return  this.repo.findAll();
    }
    public Set<E> buscarEntidadesSet(){
        return  new HashSet<>(this.repo.findAll());
    }

    public Set<DTO> buscarTodosSet(){

        return  new HashSet<>(this.serviceMapper.toDto(this.repo.findAll()));
    }

    public Page<DTO> buscarTodos(Pageable pageable){
        return  repo.findAll(pageable).map(this.serviceMapper::toDto);
    }
    public Page<DTO> buscarTodosAux(Pageable pageable){
        Page<E> pageEntity;
        pageEntity= repo.findAll(pageable);
        return  pageEntity.map(this.serviceMapper::toDto);
    }
    public Page<E> buscarTodosAuxEnt(Pageable pageable){
        Page<E> pageEntity;
        pageEntity= repo.findAll(pageable);
        return  pageEntity;
    }

    //Buscar por id
    public Optional<DTO> encuentraPorId(ID id){

        return this.repo.findById(id).map(this.serviceMapper::toDto);
    }
    public Optional<E> encuentraPorIdEntity(ID id){

        return this.repo.findById(id);
    }
    //Guardar
    public DTO guardar(DTO dto) throws Exception {
        //Traduzco del dto con datos de entrada a la entidad
        final E entidad = serviceMapper.toEntity(dto);
        //Guardo el la base de datos
        E entidadGuardada =  repo.save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return serviceMapper.toDto(entidadGuardada);
    }
    //Guardar
    public DTO guardarEntidadDto(E entidad)  {
        //Guardo el la base de datos
        E entidadGuardada =  repo.save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return serviceMapper.toDto(entidadGuardada);
    }
    //Guardar
    public E guardarEntidadEntidad(E entidad)  {
        //Guardo el la base de datos
        return repo.save(entidad);
    }
    public void  guardar(List<DTO> dtos) throws Exception {
        Iterator<DTO> it = dtos.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            E e = serviceMapper.toEntity(it.next());
            repo.save(e);
        }
    }
    //eliminar un registro
    public void eliminarPorId(ID id){
        this.repo.deleteById(id);
    }
    //Obtener el mapper
    public MAPPER getMapper(){return  serviceMapper;}
    //Obtener el repo
    public REPO getRepo(){return  repo;}
}
