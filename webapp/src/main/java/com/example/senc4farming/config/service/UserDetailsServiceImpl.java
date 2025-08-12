package com.example.senc4farming.config.service;


import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.model.Role;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.repository.UsuarioRepository;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.util.Collection;
import java.util.Set;


/**
 * Esta clase es una implementación personalizada de UserDetailsService para manejar
 * la autenticación de usuarios en la aplicación. Utiliza el UserRepository para
 * buscar y cargar la información del usuario en la base de datos.
 * <br>
 * Es una implementación de la interfaz UserDetailsService de Spring Security.
 * Su propósito es proporcionar una forma de cargar y devolver los detalles del usuario en un objeto UserDetails,
 * que es necesario para la autenticación y autorización en Spring Security.
 * <br>
 * En resumen, esta clase se utiliza para cargar los detalles de usuario
 * (como el nombre de usuario, la contraseña y los roles)
 * desde el repositorio de usuarios de la aplicación y devolverlos en un objeto
 * UserDetails para ser utilizado por Spring Security en la autenticación y autorización de los usuarios.
 */
@Service
public class UserDetailsServiceImpl implements UserDetailsService {


    private final UsuarioRepository userRepository; // Inyección de dependencia del UserRepository

    public UserDetailsServiceImpl(UsuarioRepository userRepository) {
        this.userRepository = userRepository;
    }


    /**
     * Este método es utilizado por Spring Security para buscar y cargar el usuario en función del
     * email proporcionado.
     *
     * @param email Email del usuario a buscar.
     * @return UserDetails Una instancia de UserDetails con los datos del usuario encontrado.
     * @throws UsernameNotFoundException Excepción lanzada si no se encuentra ningún usuario con el email proporcionado.
     */
    @Override
    public SuperCustomerUserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        // Buscar el usuario por su email utilizando el UserRepository
        Usuario user = userRepository.findByEmailAndActiveTrue(email);

        // Si el usuario es encontrado, crear una instancia de nuestro Custom UserDetails utilizando los datos del
        // usuario
        SuperCustomerUserDetails superCustomerUserDetails = new SuperCustomerUserDetails();
        if (user != null) {

            superCustomerUserDetails.setUsername(email);
            superCustomerUserDetails.setPassword(user.getPassword());
            superCustomerUserDetails.setCoperClientSecret("");
            superCustomerUserDetails.setCoperClientId("");
            superCustomerUserDetails.setCoperPassword("");
            superCustomerUserDetails.setCoperUsername("");
            superCustomerUserDetails.setAuthorities(mapRolesToAuthorities(user.getRoles()));
            superCustomerUserDetails.setUserID( Math.toIntExact(user.getId()));
            superCustomerUserDetails.setUsuario(user);
            //creamos la clave pulbico/privada
            KeyPairGenerator keyPairGenerator = null;
            try {
                keyPairGenerator = KeyPairGenerator.getInstance("RSA");
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException(e);
            }
            keyPairGenerator.initialize(2048);
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            user.setPublickey(keyPair.getPublic().getEncoded());
            userRepository.save(user);

            superCustomerUserDetails.setPrivatekey(keyPair.getPrivate());
            superCustomerUserDetails.setPublickey(keyPair.getPublic());
            //Actualikzamos usuario con clave publica


        }else{
            // Si el usuario no es encontrado, lanzar una excepción UsernameNotFoundException
            superCustomerUserDetails.setUsername("anonimo@anonimo");
            superCustomerUserDetails.setCoperClientSecret("");
            superCustomerUserDetails.setCoperClientId("");
            superCustomerUserDetails.setCoperPassword("");
            superCustomerUserDetails.setCoperUsername("");
        }
        return superCustomerUserDetails;
    }

    /**
     * Esta función auxiliar se utiliza para convertir la lista de roles del usuario en una colección de
     * autoridades que pueden ser utilizadas por Spring Security.
     *
     * @param roles Lista de roles del usuario.
     * @return Collection< ? extends GrantedAuthority> Colección de autoridades.
     */
    private Collection < ? extends GrantedAuthority> mapRolesToAuthorities(Set<Role> roles) {
        // Utilizar streams de Java para mapear cada rol a una instancia de SimpleGrantedAuthority
        return roles.stream()
                .map(role -> new SimpleGrantedAuthority(role.getRoleName()))
                .toList(); // Convertir el stream en una lista
    }



}

