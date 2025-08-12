package com.example.senc4farming.service;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.*;

public abstract class AbstractBusinessServiceSoloEnt<E, I,  R extends JpaRepository<E,I>>  {
    private final R repo;



    protected AbstractBusinessServiceSoloEnt(R repo) {
        this.repo = repo;

    }

    public List<E> buscarEntidades(){
        return  this.repo.findAll();
    }
    public Set<E> buscarEntidadesSet(){
        return   new HashSet<>(this.repo.findAll());
    }

    public Optional<E> encuentraPorIdEntity(I id){

        return this.repo.findById(id);
    }
    public Optional<E> encuentraPorId(I id){

        return this.repo.findById(id);
    }
    public Page<E> buscarTodos(Pageable pageable){
        return  repo.findAll(pageable);
    }

    //Guardar
    public E guardar(E entidad) {
        //Guardo el la base de datos
        return repo.save(entidad);
    }
    public void  guardar(List<E> ents )  {
        Iterator<E> it = ents.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            E e = it.next();
            repo.save(e);
        }
    }
    //eliminar un registro
    public void eliminarPorId(I id){
        this.repo.deleteById(id);
    }
    //Obtener el repo
    public R getRepo(){return  repo;}
}
