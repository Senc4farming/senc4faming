package com.example.senc4farming.controller;

import com.example.senc4farming.config.details.SuperCustomerUserDetails;
import com.example.senc4farming.dto.BloqueDto;
import com.example.senc4farming.model.Usuario;
import com.example.senc4farming.service.MenuService;
import com.example.senc4farming.service.UsuarioService;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;


/**
 * Controlador de la funcionalidad Blockchain de la aplicación.
 * Aquí gestionamos la creación y visualización de bloques que simulan una cadena de bloques simple.
 */
@Controller
@RequestMapping("/blockchain")
public class AppBlockchainController  extends AbstractController <BloqueDto>{
    private final UsuarioService service;


    public AppBlockchainController(MenuService menuService, UsuarioService service) {
        super(menuService);
        this.service = service;
        /**
         * Constructor que inicializa el primer bloque (bloque génesis) al arrancar la aplicación.
         */
        Charset charset =  StandardCharsets.UTF_8;
        String cadenainicial = "Bloque principal";
        byte[] byteArrray = cadenainicial.getBytes(charset);
        blockchain.add(new BloqueDto(0,0,byteArrray, "0"));
    }
    /**
     * Lista que representa nuestra cadena de bloques.
     */
    private final List<BloqueDto> blockchain = new ArrayList<>();

    /**
     * Muestra la página de la cadena de bloques con los bloques actuales y una indicación de validez.
     * @param model Objeto para pasar atributos a la vista
     * @return nombre de la plantilla HTML "blockchain"
     */
    @GetMapping
    public String verBlockchain(Model model) throws NoSuchAlgorithmException, InvalidKeySpecException, NoSuchPaddingException, InvalidKeyException, IllegalBlockSizeException, BadPaddingException {
        //Desencriptamos todos los datos iterando sobre la lista
        Iterator<BloqueDto> it = blockchain.iterator();

        List<BloqueDto> listadecodificada = new ArrayList<>();
        // traduzco con clave publica
        while(it.hasNext()) {
            BloqueDto dto = it.next();
            if (dto.getUserid() > 0){
                byte[] decoded = decryptPublicKeys((int) dto.getUserid(), dto.getDatos());
                dto.setDatos(decoded);
            }
            listadecodificada.add(dto);
        }


        model.addAttribute("blockchain", listadecodificada);
        model.addAttribute("valida", esCadenaValida());
        return "blockchain/show";
    }
    /**
     * Verifica si la cadena de bloques es válida comprobando los hashes.
     * @return true si la cadena es válida, false en caso contrario
     */
    public boolean esCadenaValida() {
        for (int i = 1; i < blockchain.size(); i++) {
            BloqueDto actual = blockchain.get(i);
            BloqueDto anterior = blockchain.get(i-1);

            if (!actual.getHash().equals(actual.calcularHash())) {
                return false;
            }

            if (!actual.getHashAnterior().equals(anterior.getHash())) {
                return false;
            }
        }
        return true;
    }
    /**
     * Agrega un nuevo bloque con los datos proporcionados por el usuario.
     * @param datos Contenido del nuevo bloque
     * @return redirección a la vista actualizada de la cadena
     */
    @PostMapping("/agregar")
    public String agregarBloque(@RequestParam String datos) throws NoSuchPaddingException, NoSuchAlgorithmException, IllegalBlockSizeException, BadPaddingException, InvalidKeyException {
        //Obtengo el último bloque
        BloqueDto ultimo = blockchain.get(blockchain.size()-1);
        //Nuevo indice
        int nuevoIndice = blockchain.size();
        //Encriptar el string datos
        Charset charset =  StandardCharsets.UTF_8;
        byte[] byteArrray = datos.getBytes(charset);

        //Nuevo bloque para la cadena
        BloqueDto nuevo = new BloqueDto(nuevoIndice,
                ((SuperCustomerUserDetails)SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUserID()
                , encryptImageWithHerPrivateKey(byteArrray), ultimo.getHash());
        //Añadirlo a la lista
        blockchain.add(nuevo);
        return "redirect:/blockchain";
    }
    // Digital signature of our Hash image . ()
    public byte[] encryptImageWithHerPrivateKey(byte[] hash) throws NoSuchAlgorithmException, NoSuchPaddingException, IllegalBlockSizeException, BadPaddingException, InvalidKeyException {
        try{
            Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWITHSHA-256ANDMGF1PADDING");
            cipher.init(Cipher.ENCRYPT_MODE, ((SuperCustomerUserDetails)SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getPrivatekey());
            return cipher.doFinal(hash);
        } catch(NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException
                | IllegalBlockSizeException | BadPaddingException e) {
            logger.error(e.getMessage());
            throw e;
        }
    }

    public  byte[] decryptPublicKeys(Integer id, byte[] encryptedPublic ) throws NoSuchAlgorithmException, InvalidKeySpecException, NoSuchPaddingException, InvalidKeyException, IllegalBlockSizeException, BadPaddingException {
        //Buscamos el usuario
        Optional<Usuario> usuario = service.buscar(id);
        if (usuario.isPresent()) {
            //obtenemos la clave pública
            PublicKey publicKey =
                    KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(usuario.get().getPublickey()));
            //Desencriptamos
            try {
                Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWITHSHA-256ANDMGF1PADDING");
                cipher.init(Cipher.DECRYPT_MODE, publicKey);
                return cipher.doFinal(encryptedPublic);
            } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException | IllegalBlockSizeException | BadPaddingException e) {
                logger.error(e.getMessage());
                throw e;
            }
        } else {
            logger.warn("User not found");
            byte[] bytes = {};
            return  bytes;
        }
    }
}
