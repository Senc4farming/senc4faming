package com.example.senc4farming.util;

import org.springframework.context.annotation.Bean;

import java.util.regex.Pattern;

public class ValidarFormatoPassword {
    private ValidarFormatoPassword(){

    }
    // Contraseña de 4-8 caracteres que requiere números y letras de ambos casos

    // Contraseña de 4 a 32 caracteres que requiere al menos 3 de 4 (mayúsculas
    // y letras minúsculas, números y caracteres especiales) y como máximo
    // 2 caracteres consecutivos iguales.
    private static final String COMPLEX_PASSWORD_REGEX =
            "^(?:(?=.*\\d)(?=.*[A-Z])(?=.*[a-z])|" +
                    "(?=.*\\d)(?=.*[^A-Za-z0-9])(?=.*[a-z])|" +
                    "(?=.*[^A-Za-z0-9])(?=.*[A-Z])(?=.*[a-z])|" +
                    "(?=.*\\d)(?=.*[A-Z])(?=.*[^A-Za-z0-9]))(?!.*(.)\\1{2,})" +
                    "[A-Za-z0-9!~<>,;:_=?*+#.\"&§%°()\\|\\[\\]\\-\\$\\^\\@\\/]" +
                    "{8,32}$";

    private static final Pattern PASSWORD_PATTERN =
            Pattern.compile(COMPLEX_PASSWORD_REGEX);
    @Bean
    public static boolean validarformato(String password){
        // Validar una contraseña
        return  PASSWORD_PATTERN.matcher(password).matches();
    }
}
