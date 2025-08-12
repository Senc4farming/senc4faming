package com.example.senc4farming.service.mapper;


import java.util.*;
import java.util.stream.Collectors;

public abstract class AbstractServiceMapper<E,D> {
    //Convertir de entidad a dto
    public abstract D toDto(E e);

    //Convertir de dto a entidad
    public abstract E toEntity(D dto) throws Exception;

    //Conversion de listas de dtos a entidades
    public List<E>  toEntity(List<D> dtos) throws Exception {
        //Recorrer la lista manualmente para gestional las excepciopnes
        ListIterator<D> it = dtos.listIterator();
        List<E> list = new ArrayList<>();
        while (it.hasNext()){
            D dto = it.next();
            E e = this.toEntity(dto);
            list.add(e);
        }
        return list;
    }
    //Conversion de listas de entidades a DTOs
    public List<D>  toDto(List<E> e){
        return e.stream().map(this::toDto).toList();
    }

    //Gestionamos set de datos
    public Set<E> toEntity(Set<D> dtos) throws Exception {

        Set<E> eSet = new HashSet<>();
        for (D item: dtos) {
            E e = this.toEntity(item);
            eSet.add(e);
        }
        return  eSet;
    }
    //Conversion de listas de entidades a DTOs
    public Set<D>  toDto(Set<E> e){
        return e.stream().map(this::toDto).collect(Collectors.toSet());
    }
}
