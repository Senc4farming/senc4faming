package com.example.senc4farming.service;


import com.example.senc4farming.dto.UsuarioDto;

import com.example.senc4farming.dto.UsuarioDtoPsw;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.repository.UsuarioRepository;
import com.example.senc4farming.service.mapper.UsuarioMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import java.util.Iterator;
import java.util.List;


@Service
public class UsuarioService   extends AbstractBusinessService<Usuario,Integer,UsuarioDto,
        UsuarioRepository,UsuarioMapper >   {
    //


    //Acceso a los datos de la bbdd
    public UsuarioService(UsuarioRepository repo, UsuarioMapper serviceMapper) {

        super(repo, serviceMapper);
    }
    public UsuarioDto guardar(UsuarioDto usuarioDto, String password){
        logger.info("usuarioDto:  %s" ,usuarioDto.getNombreUsuario() );
        //Traduzco del dto con datos de entrada a la entidad
        final Usuario entidad = getMapper().toEntity(usuarioDto);
        logger.info("Entidad:  %s" ,entidad.getNombreUsuario() );
        entidad.setPassword(password);
        logger.info("Entidad: %s" ,entidad.getPassword() );
        //Guardo el la base de datos
        Usuario entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }
    public UsuarioDto guardar(UsuarioDtoPsw usuarioDtoPsw){
        logger.info("usuarioDto %s" ,usuarioDtoPsw.getNombreUsuario() );
        //Traduzco del dto con datos de entrada a la entidad
        final Usuario entidad = getMapper().toEntityPsw(usuarioDtoPsw);
        logger.info("Entidad: %s" ,entidad.getNombreUsuario() );
        //Guardo el la base de datos
        Usuario entidadGuardada =  getRepo().save(entidad);
        //Traducir la entidad a DTO para devolver el DTO
        return getMapper().toDto(entidadGuardada);
    }
    //Método para guardar una lista de usuarios
    //La entrada es una lista de DTO ( que viene de la pantalla)
    //La respuesta tipo void
    @Override
    public void  guardar(List<UsuarioDto> lUsuarioDto){
        Iterator<UsuarioDto> it = lUsuarioDto.iterator();

        // mientras al iterador queda proximo juego
        while(it.hasNext()){
            //Obtenemos la password de a entidad
            //Datos del usuario
            Usuario usuario = getMapper().toEntity(it.next());
            usuario.setPassword(getRepo().getReferenceById((int) usuario.getId()).getPassword());
            getRepo().save(usuario);
        }
    }

    public Page<UsuarioDto> buscarTodosPorEmail(Pageable pageable, String email){
        return  getRepo().findUsuarioByEmailLike(email,pageable).map(getMapper()::toDto);
    }

}
