package com.example.sen4farming.dto;

import com.example.sen4farming.model.Usuario;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class EvalScriptDto {

    private Integer id;
    private String scriptTitle;
    private String scriptDescription;
    private String scriptText;
    private boolean shared = true;
    private Usuario usuarioScript;

}
