package com.example.sen4farming.dto;

import lombok.Getter;
import lombok.Setter;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;

@Getter
@Setter
public class BloqueDto {
    private int indice;
    private byte[] datos;
    private long userid;
    private String hashAnterior;
    private String hash;

    public BloqueDto(int indice,Integer id, byte[] datos, String hashAnterior) {
        this.indice = indice;
        this.userid = id;
        this.datos = datos;
        this.hashAnterior = hashAnterior;
        this.hash = calcularHash();
    }

    public String calcularHash() {
        try {
            String contenido = indice + Arrays.toString(datos) + hashAnterior;
            MessageDigest digest = MessageDigest.getInstance("SHA3-512");
            byte[] hashBytes = digest.digest(contenido.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            return null;
        }
    }
    public String getdatosbyte(){
        return this.hash;

    }
}
