package com.example.sen4farming.service;


import com.example.sen4farming.dto.MenuDTO;
import com.example.sen4farming.model.AyudaUsr;
import com.example.sen4farming.model.Menu;
import com.example.sen4farming.model.Role;
import com.example.sen4farming.model.Usuario;
import com.example.sen4farming.repository.AyudaUsrRepository;
import com.example.sen4farming.repository.MenuRepository;
import com.example.sen4farming.repository.RoleRepository;
import com.example.sen4farming.repository.UsuarioRepository;
import com.example.sen4farming.service.mapper.MenuServiceMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Service
public class MenuService extends AbstractBusinessService<Menu, Integer, MenuDTO, MenuRepository, MenuServiceMapper> {

    private final UsuarioRepository usuarioRepository;
    private final RoleRepository roleRepository;

    private final AyudaUsrRepository ayudaUsrRepository;


    @Autowired
    protected MenuService(MenuRepository repository, MenuServiceMapper serviceMapper,
                          UsuarioRepository usuarioRepository, RoleRepository roleRepository, AyudaUsrRepository ayudaUsrRepository) {
        super(repository, serviceMapper);
        this.usuarioRepository = usuarioRepository;
        this.roleRepository = roleRepository;
        this.ayudaUsrRepository = ayudaUsrRepository;
    }

    public List<MenuDTO> getMenuForUsuarioId(Integer usuarioId) {
        Usuario usuario = this.usuarioRepository.findById(usuarioId)
                .orElseThrow(() -> new RuntimeException(String.format("The user ID %s does not exist", usuarioId)));
        return getMenuForRole(usuario.getRoles());
    }

    public List<MenuDTO> getMenuForRole(Collection<Role> roles) {
        List<Menu> menus = this.getRepo().findDistinctByRolesInAndActiveTrueOrderByOrder(roles);
        return this.getMapper().toDto(menus);
    }

    public List<MenuDTO> getMenuForEmail(String email) {
        Usuario usuario = this.usuarioRepository.findByEmailAndActiveTrue(email);
        return getMenuForRole(usuario.getRoles());
    }

    public String ayudatitulo (String  url){
        Optional<AyudaUsr> ayudaUsrOptional = this.ayudaUsrRepository.findAyudaUsrByUrl(url);
        if (ayudaUsrOptional.isPresent()){
            return ayudaUsrOptional.get().getTitle();
        }else {
            return("Not found");
        }
    }
    public String ayudadesc (String  url){
        Optional<AyudaUsr> ayudaUsrOptional = this.ayudaUsrRepository.findAyudaUsrByUrl(url);
        if (ayudaUsrOptional.isPresent()){
            return ayudaUsrOptional.get().getDescription();
        }else {
            return("Not found");
        }
    }
    public String ayudabody (String  url){
        Optional<AyudaUsr> ayudaUsrOptional = this.ayudaUsrRepository.findAyudaUsrByUrl(url);
        if (ayudaUsrOptional.isPresent()){
            return ayudaUsrOptional.get().getBody();
        }else {
            return("Not found");
        }
    }
}
