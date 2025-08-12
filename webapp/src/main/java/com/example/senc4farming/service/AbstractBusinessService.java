package com.example.senc4farming.service;

import com.example.senc4farming.service.mapper.AbstractServiceMapper;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.*;

public abstract class AbstractBusinessService   <E, I, D,  R extends JpaRepository<E,I> ,
        M extends AbstractServiceMapper<E,D>>  {
    private final R repo;
    private final M serviceMapper;

    Logger logger = LogManager.getLogger(this.getClass());


    protected AbstractBusinessService(R repo, M mapper) {
        this.repo = repo;
        this.serviceMapper = mapper;
    }
    //Buscamos por id sin optional
    public E buscarSinOpt(I id){return  this.repo.getReferenceById(id);}
    public D buscarDtoSinOpt(I id){return  this.serviceMapper.toDto(this.repo.getReferenceById(id));}
    //Buscamos por id
    public Optional<E> buscar(I id){return  this.repo.findById(id);}
    //Lista de todos los DTOs buscarTodos devolvera lista y paginas
    public List<D> buscarTodos(){
        logger.info("pepe");
        return  this.serviceMapper.toDto(this.repo.findAll());
    }

    public List<E> buscarEntidades(){
        return  this.repo.findAll();
    }
    public Set<E> buscarEntidadesSet(){
        return  new HashSet<>(this.repo.findAll());
    }

    public Set<D> buscarTodosSet(){

        return  new HashSet<>(this.serviceMapper.toDto(this.repo.findAll()));
    }

    public Page<D> buscarTodos(Pageable pageable){
        return  repo.findAll(pageable).map(this.serviceMapper::toDto);
    }
    public Page<D> buscarTodosAux(Pageable pageable){
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
    public Optional<D> encuentraPorId(I id){

        return this.repo.findById(id).map(this.serviceMapper::toDto);
    }
    public Optional<E> encuentraPorIdEntity(I id){

        return this.repo.findById(id);
    }
    //Guardar
    public D guardar(D dto) throws Exception {
        //Traduzco del D con datos de entrada a la entidad
        final E entidad = serviceMapper.toEntity(dto);
        //Guardo el la base de datos
        E entidadGuardada =  repo.save(entidad);
        //Traducir la entidad a D para devolver el DTO
        return serviceMapper.toDto(entidadGuardada);
    }
    //Guardar
    public D guardarEntidadDto(E entidad)  {
        //Guardo el la base de datos
        E entidadGuardada =  repo.save(entidad);
        //Traducir la entidad a D para devolver el DTO
        return serviceMapper.toDto(entidadGuardada);
    }
    //Guardar
    public E guardarEntidadEntidad(E entidad)  {
        //Guardo el la base de datos
        return repo.save(entidad);
    }
    public void  guardar(List<D> dtos) throws Exception {
        Iterator<D> it = dtos.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            E e = serviceMapper.toEntity(it.next());
            repo.save(e);
        }
    }
    //eliminar un registro
    public void eliminarPorId(I id){
        this.repo.deleteById(id);
    }
    //Obtener el mapper
    public M getMapper(){return  serviceMapper;}
    //Obtener el repo
    public R getRepo(){return  repo;}
}
